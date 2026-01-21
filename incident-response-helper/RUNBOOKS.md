# Incident Runbooks

Quick reference for common production incidents.

---

## Database Issues

### Connection Pool Exhaustion

**Symptoms:** 500 errors, "connection pool exhausted", slow queries

**Diagnosis:**

```bash
# Check active connections (PostgreSQL)
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
```

**Resolution:**

1. Increase pool size temporarily (HikariCP, pg_pool)
2. Find and fix leaking connections (missing `.close()`)
3. Add connection timeouts
4. Consider read replicas for read-heavy workloads

### Replication Lag

**Symptoms:** Stale data on reads, inconsistent query results

**Diagnosis:**

```sql
-- PostgreSQL
SELECT pg_last_wal_receive_lsn() - pg_last_wal_replay_lsn() AS replication_lag;
```

**Resolution:**

1. Check replica disk I/O and CPU
2. Reduce write load on primary
3. Increase replica resources
4. Check network between primary and replica

---

## Memory/CPU Issues

### Out of Memory (OOM)

**Symptoms:** Process killed, OOMKilled in k8s, sudden restart

**Diagnosis:**

```bash
# Check k8s OOM events
kubectl describe pod <pod> | grep -i oom
# Check memory usage
kubectl top pods
```

**Resolution:**

1. Increase memory limits (temporary)
2. Find memory leak with profiler
3. Add memory monitoring/alerts
4. Implement pagination for large datasets

### High CPU

**Symptoms:** Slow responses, timeouts, 100% CPU

**Diagnosis:**

```bash
# Top processes
top -c
# Thread dump (Java)
jstack <pid>
```

**Resolution:**

1. Identify hot path (profiler/flame graph)
2. Check for infinite loops
3. Optimize algorithmic complexity
4. Add caching for expensive computations

---

## Network Issues

### DNS Resolution Failures

**Symptoms:** "Unknown host", intermittent connection failures

**Diagnosis:**

```bash
nslookup <hostname>
dig <hostname>
```

**Resolution:**

1. Check DNS server health
2. Increase DNS TTL
3. Add retry with exponential backoff
4. Consider DNS caching layer

### Connection Timeouts

**Symptoms:** Slow or hanging requests, connection refused

**Diagnosis:**

```bash
# Test connectivity
curl -v --connect-timeout 5 <url>
telnet <host> <port>
```

**Resolution:**

1. Check target service health
2. Verify network/firewall rules
3. Check load balancer configuration
4. Review connection pool settings

---

## Deployment Failures

### Rollback Procedure

1. **Identify last good version**

   ```bash
   git log --oneline -10
   kubectl rollout history deployment/<name>
   ```

2. **Execute rollback**

   ```bash
   # Kubernetes
   kubectl rollout undo deployment/<name>
   # Or specific revision
   kubectl rollout undo deployment/<name> --to-revision=<n>
   ```

3. **Verify rollback**
   ```bash
   kubectl rollout status deployment/<name>
   ```

### Container Won't Start

**Symptoms:** CrashLoopBackOff, ImagePullBackOff

**Diagnosis:**

```bash
kubectl describe pod <pod>
kubectl logs <pod> --previous
```

**Resolution:**

- ImagePullBackOff: Check image name, registry auth
- CrashLoopBackOff: Check application logs, entrypoint

---

## Security Incidents

### Credential Exposure

**Immediate actions:**

1. **Rotate credentials immediately**
2. Revoke exposed tokens/keys
3. Audit access logs for unauthorized use
4. Update secrets in vault/k8s

### Unusual Access Patterns

**Detection:**

- Logins from new locations
- High API call volume
- Access to sensitive endpoints

**Response:**

1. Capture evidence (logs, screenshots)
2. Block suspicious IPs if confirmed malicious
3. Reset affected user sessions
4. Notify security team
