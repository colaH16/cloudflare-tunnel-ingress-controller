# PR #368 runtime evidence

The Prefix fix was tested against real Cloudflare Tunnel traffic before the production rollout. One isolated Ingress was retained across the controller-image switch. All 20 final HTTP cases matched the intended patched backend; ImplementationSpecific regex behavior was preserved.

- [Actual request and generated-regex comparison](runtime-results.md)
- [Before responses and sanitized Cloudflare rules](http-demo-before.json)
- [After responses and sanitized Cloudflare rules](http-demo-after.json)
- [Recorded-results terminal replay](http-results-replay.cast) — `asciinema play http-results-replay.cast`
- [Standalone result viewer](http-results-replay.html) — download and open locally
- [Startup/propagation observations](test-observations.json)
- [Image build run](https://github.com/colaH16/cloudflare-tunnel-ingress-controller/actions/runs/36580110382)
- [Image digests and source revisions](published-images.json)
- [Reusable image workflow](https://github.com/colaH16/cloudflare-tunnel-ingress-controller/actions/workflows/build-test-image.yaml) — Run workflow, select `source_ref`, optionally build the pre-fix baseline. GHCR publishing uses the automatically issued GITHUB_TOKEN with packages:write; no personal token is required.

The replay is generated from saved actual request observations. It is not presented as a live terminal recording or a continuously running test endpoint.

## Automated checks

- The new Ingress-to-Exposure regression test: 8 table-driven cases passed with the race detector.
- Full `go test -race ./pkg/...`: passed.
- Kubernetes envtest integration: 17/17 specs passed with the race detector.
- Changed-code golangci-lint: 0 issues. Full lint still reports the same two pre-existing SA1019 deprecations on the clean upstream baseline; those unrelated warnings were not changed.
- The patched multi-architecture image was rolled out sequentially to 6 controllers across AMD64 and ARM64 nodes. All 45 existing routes were revalidated for unchanged backends, origin settings, DNS ownership and placement. All 45 public HTTP statuses and sanitized redirect targets matched the baseline, including pre-existing non-2xx responses. All 25 existing Traefik Ingress UIDs, specifications and annotations were unchanged. See [production regression summary](production-regression-summary.json).

## Test environment and reproduction

The test uses a separate Cloudflare Tunnel and IngressClass, three static echo backends, and one Kubernetes Ingress. Only the controller image changes between the final before and after runs. No production hostname is used for the echo test.

The baseline is upstream master `627362f269d42ae4cb7fdfba1933d9bb078a95b0`. The patch is PR #368 commit `ed40cb12cf32d7b7315f71b66831c92bca3fd2b4`. Both use the upstream Dockerfile and a pinned distroless runtime, built on GitHub Actions with its automatically issued GITHUB_TOKEN. There are AMD64 and ARM64 patch images; the baseline comparison runs on AMD64.

The local race tests use Go 1.26.5 and envtest Kubernetes 1.36.2. The Actions Dockerfile currently resolves its `golang:1.26` builder to Go 1.26.8. These build environments are recorded separately.

## Reproduction

1. Use a separate test Tunnel and an unused public hostname. Create a `cloudflare-api` Secret in namespace `pr368-path-test` with the chart's `api-token`, `cloudflare-account-id`, and `cloudflare-tunnel-name` keys, using your own account.
2. Apply `echo-backends.yaml`. Render/deploy the official STRRL 0.1.0 Helm chart with `baseline-controller-values.yaml` in that namespace. Change `test.example.com` in `ingress-path-matching.yaml` to your test hostname and apply the Ingress after the controller and connector are ready.
3. Wait for the new hostname and tunnel to become reachable. Record the generated tunnel path expressions and run `python3 probe-results.py YOUR_TEST_HOSTNAME --output before.json`. The echo bodies identify the selected backend: PUBLIC, ADMIN, or LITERAL.
4. Upgrade the same chart release using `patched-controller-values.yaml`. Keep the Ingress unchanged. After the controller is ready and Cloudflare has received the new configuration, repeat the same requests with `python3 probe-results.py YOUR_TEST_HOSTNAME --output after.json`.
5. Confirm all Prefix matches obey segment boundaries, anchors, trailing-slash normalization, and literal metacharacters. Confirm ImplementationSpecific retains the previous regex behavior. Remove only the isolated test resources and test Tunnel after recording the results.

The runtime reports contain only request paths, timestamps, statuses, backend labels, and sanitized tunnel path expressions. They exclude credentials, production hosts, account IDs, and Tunnel UUIDs.
