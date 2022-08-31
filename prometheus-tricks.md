. 
    - name: pod_disk_usage
      rules:

      - alert: pod disk is full.
        # max/avg/min to deduplicate.
        expr: (0 * kube_pod_spec_volumes_persistentvolumeclaims_info) + on(persistentvolumeclaim) group_left 100* ( max(kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) by (persistentvolumeclaim)) > 85
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: pod disk is full
          description: "Pod disk is full\nValue = {{ $value }}\nLabels = {{ $labels.env }}"

