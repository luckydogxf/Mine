1. group_left的时候，一边有多个重复的metric. 例如利用`cephfs`的时候，就有这种情况，此时就会出错，用avg/min/max可以dedupicate。
```

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
```

2. 某些metric只有特定条件下才有值，例如ceph OSD，只有down的时候，才会有值，那应该怎么处理呢？`vector(x)` 可以返回x

```
count(ceph_osd_up{app="$cluster"} ==0) OR vector(0)

```
