WORKFLOW_AND_K8S_CONFIG = r"""
# .github/workflows/prometheus-rules-test.yml
name: Full CI/CD, Observability, and External-Metric HPA

on:
  push:
    branches: [ main ]
  pull_request:
  schedule:
    - cron: "0 2 * * *"

env:
  K8S_NAMESPACE: lando

jobs:
  tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        prometheus_version: ["2.44.0", "2.46.0", "2.47.0"]
    steps:
      - uses: actions/checkout@v3

      - uses: actions/cache@v3
        id: cache-promtool
        with:
          path: /usr/local/bin/promtool
          key: promtool-${{ matrix.prometheus_version }}

      - if: steps.cache-promtool.outputs.cache-hit != 'true'
        run: |
          curl -sL https://github.com/prometheus/prometheus/releases/download/v${{ matrix.prometheus_version }}/prometheus-${{ matrix.prometheus_version }}.linux-amd64.tar.gz | tar xz
          sudo mv prometheus-${{ matrix.prometheus_version }}.linux-amd64/promtool /usr/local/bin/

      - uses: actions/cache@v3
        id: cache-pip
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: ${{ runner.os }}-pip-

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov codecov

      - run: promtool check rules helm/templates/prometheus-rules.yaml

      - run: |
          cat > /tmp/rule-tests.yaml <<'EOF'
          rule_files:
            - helm/templates/prometheus-rules.yaml
          tests:
            - interval: 1m
              input_series:
                - series: 'http_requests_total{status="500"}'
                  # Explicit numeric samples instead of shorthand like 1+1x5
                  values: "1 2 3 4 5 6"
              alert_rule_test:
                - alertname: HighErrorRate
                  exp_alerts:
                    - exp_labels:
                        severity: critical
                      exp_annotations:
                        summary: "High error rate on Lando API"

            - interval: 1m
              input_series:
                - series: 'http_request_duration_seconds_bucket{le="1"}'
                  values: "2 4 6 8 10 12"
              alert_rule_test:
                - alertname: HighLatency
                  exp_alerts:
                    - exp_labels:
                        severity: warning
                      exp_annotations:
                        summary: "High latency on Lando API"

            - interval: 1m
              input_series:
                - series: 'kube_pod_container_status_restarts_total{pod="lando-0"}'
                  values: "0 1 2 3 4 5 6 7 8 9 10"
              alert_rule_test:
                - alertname: PodRestarts
                  exp_alerts:
                    - exp_labels:
                        severity: warning
                      exp_annotations:
                        summary: "Lando pod is restarting frequently"

            - interval: 1m
              input_series:
                - series: 'lando_secret_fallback_total'
                  values: "0 1 2 3 4 5"
              alert_rule_test:
                - alertname: SecretFallbackActivated
                  exp_alerts:
                    - exp_labels:
                        severity: warning
                      exp_annotations:
                        summary: "Lando secret fallback was activated"

            - interval: 1m
              input_series:
                - series: 'container_cpu_usage_seconds_total{pod="lando-0"}'
                  values: "0 5 10 15 20 25"
              alert_rule_test:
                - alertname: HighCPUUsage
                  exp_alerts:
                    - exp_labels:
                        severity: warning
                      exp_annotations:
                        summary: "High CPU usage detected"

            # Additional negative test to ensure alert does NOT fire
            - interval: 1m
              input_series:
                - series: 'http_requests_total{status="500"}'
                  values: "0 0 0 0 0 0"
              alert_rule_test:
                - alertname: HighErrorRate
                  exp_alerts: []
          EOF
          promtool test rules /tmp/rule-tests.yaml

      - run: pytest --cov=. --cov-report=xml --cov-fail-under=80

      - uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  deploy:
    needs: tests
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3

      - uses: azure/setup-kubectl@v3
        with:
          version: 'v1.27.0'

      - uses: azure/setup-helm@v3
        with:
          version: 'v3.12.0'

      - name: Configure kubeconfig
        run: |
          mkdir -p ~/.kube
          echo "${KUBECONFIG_DATA}" | base64 --decode > ~/.kube/config
        env:
          KUBECONFIG_DATA: ${{ secrets.KUBECONFIG_DATA }}

      - id: start
        run: echo "start_time=$(date +%s)" >> $GITHUB_OUTPUT

      - name: Deploy Lando (Helm)
        run: |
          helm upgrade --install lando ./helm \
            --namespace $K8S_NAMESPACE \
            --create-namespace \
            --set image.tag=${{ github.sha }}

# helm/templates/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "lando.fullname" . }}-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "lando.fullname" . }}
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
    - type: External
      external:
        metric:
          name: http_requests_per_pod
        target:
          type: AverageValue
          averageValue: "10"

# monitoring/prometheus-adapter-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-adapter-config
  namespace: lando
data:
  config.yaml: |
    rules:
      - seriesQuery: 'rate(http_requests_total[2m])'
        resources:
          overrides:
            pod:
              resource: pod
        name:
          as: 'http_requests_per_pod'
        metricsQuery: 'sum(rate(http_requests_total[2m])) by (pod)'

# infra/README_AUTOSCALING.md
Overview
--------
This update makes the HPA rely on an external Prometheus-derived metric (`http_requests_per_pod`) via the Prometheus Adapter. It applies an optimized HPA that combines CPU utilization and external request-load-driven scaling.

Secrets required
----------------
- KUBECONFIG_DATA (base64 kubeconfig)
- CLOUD_PROVIDER (gke|aws|azure or unset)
- CLUSTER_NAME
- SERVICE_URL
- SLACK_WEBHOOK_URL (optional)
"""
