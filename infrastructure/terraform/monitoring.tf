# ─── Cloud Monitoring ─────────────────────────────────────────────────────────

resource "google_monitoring_dashboard" "dialectica" {
  project        = var.project_id
  dashboard_json = jsonencode({
    displayName = "DIALECTICA Operations Dashboard"
    mosaicLayout = {
      columns = 12
      tiles = [
        # Row 1: API latency and request count
        {
          width  = 6
          height = 4
          widget = {
            title = "API Request Latency (p99)"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"run.googleapis.com/request_latencies\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_DELTA"
                      crossSeriesReducer = "REDUCE_PERCENTILE_99"
                    }
                  }
                }
              }]
            }
          }
        },
        {
          xPos   = 6
          width  = 6
          height = 4
          widget = {
            title = "API Request Count"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"run.googleapis.com/request_count\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                    }
                  }
                }
              }]
            }
          }
        },

        # Row 2: Extraction pipeline latency (p50, p95, p99)
        {
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Extraction Pipeline Latency (p50 / p95 / p99)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"logging.googleapis.com/user/dialectica_extraction_duration_seconds\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_DELTA"
                        crossSeriesReducer = "REDUCE_PERCENTILE_50"
                      }
                    }
                  }
                  legendTemplate = "p50"
                },
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"logging.googleapis.com/user/dialectica_extraction_duration_seconds\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_DELTA"
                        crossSeriesReducer = "REDUCE_PERCENTILE_95"
                      }
                    }
                  }
                  legendTemplate = "p95"
                },
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"logging.googleapis.com/user/dialectica_extraction_duration_seconds\""
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_DELTA"
                        crossSeriesReducer = "REDUCE_PERCENTILE_99"
                      }
                    }
                  }
                  legendTemplate = "p99"
                },
              ]
            }
          }
        },
        {
          xPos   = 6
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Active Cloud Run Instances"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"run.googleapis.com/container/instance_count\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
              }]
            }
          }
        },

        # Row 3: Error rate by response code and memory usage
        {
          yPos   = 8
          width  = 6
          height = 4
          widget = {
            title = "Error Rate by Response Code Class"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"run.googleapis.com/request_count\" metric.labels.response_code_class!=\"2xx\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields      = ["metric.labels.response_code_class"]
                    }
                  }
                }
              }]
            }
          }
        },
        {
          xPos   = 6
          yPos   = 8
          width  = 6
          height = 4
          widget = {
            title = "Memory Utilization (%)"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"run.googleapis.com/container/memory/utilizations\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_PERCENTILE_99"
                      crossSeriesReducer = "REDUCE_MAX"
                    }
                  }
                }
              }]
            }
          }
        },

        # Row 4: BigQuery event throughput
        {
          yPos   = 12
          width  = 6
          height = 4
          widget = {
            title = "BigQuery Analytics — Rows Inserted / min"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"bigquery_dataset\" resource.labels.dataset_id=\"dialectica_analytics\" metric.type=\"bigquery.googleapis.com/storage/uploaded_row_count\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                    }
                  }
                }
              }]
            }
          }
        },
      ]
    }
  })

  depends_on = [google_project_service.required_apis]
}

# ─── Alert Policies ─────────────────────────────────────────────────────────

resource "google_monitoring_alert_policy" "api_error_rate" {
  project      = var.project_id
  display_name = "DIALECTICA API High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "5xx error rate > 1%"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"run.googleapis.com/request_count\" metric.labels.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.01
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = []
  depends_on            = [google_project_service.required_apis]
}

resource "google_monitoring_alert_policy" "extraction_failure_rate" {
  project      = var.project_id
  display_name = "DIALECTICA Extraction Failure Rate > 10%"
  combiner     = "OR"

  conditions {
    display_name = "Extraction error rate exceeds 10%"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"logging.googleapis.com/user/dialectica_extraction_duration_seconds\" metric.labels.status=\"error\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.1
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = []
  depends_on            = [google_project_service.required_apis]
}

resource "google_monitoring_alert_policy" "query_latency_p99" {
  project      = var.project_id
  display_name = "DIALECTICA Query Latency p99 > 5s"
  combiner     = "OR"

  conditions {
    display_name = "Query p99 latency exceeds 5 seconds"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5000
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_99"
      }
    }
  }

  notification_channels = []
  depends_on            = [google_project_service.required_apis]
}

resource "google_monitoring_alert_policy" "memory_usage" {
  project      = var.project_id
  display_name = "DIALECTICA Memory Usage > 80%"
  combiner     = "OR"

  conditions {
    display_name = "Container memory utilization exceeds 80%"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"dialectica-api\" metric.type=\"run.googleapis.com/container/memory/utilizations\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_99"
        cross_series_reducer = "REDUCE_MAX"
      }
    }
  }

  notification_channels = []
  depends_on            = [google_project_service.required_apis]
}
