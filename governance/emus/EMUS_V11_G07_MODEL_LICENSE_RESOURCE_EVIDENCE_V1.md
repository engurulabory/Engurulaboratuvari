# EMÜS V1.1 — G07 Yerel Model, Lisans ve Kaynak Kanıt Uzlaştırması
STATE: HISTORICAL_MODEL_EVIDENCE_CONFIRMED / CURRENT_EXACT_MODEL_HOLD
DATE: 2026-10-24
SCOPE: GH-09-C2, GH-09-C3, GH-09-C4; GH-07 resources

## Gerçek mevcut ENGÜRÜ kanıtı
- Kaynak: evidence/SHARED_AI_LOCAL_RUNTIME_COMMISSIONING_2026-09-18.md (Labory main)
- Kaynağın raporladığı o dönem yerel model: Ollama qwen3:14b.
- Raporlanan gerçek yerel inference: ENGURU_LOCAL_PASS; route provider local_runtime, model qwen3:14b, estimated_cost=0.0, active_providers=1.
- Raporlanan negatif kapılar: paid route blocked, unverified privacy/commercial usage blocked, capability mismatch HOLD, runtime unavailable HOLD.
- Bu tarihsel kanıt geçmiş commissioning geçerliliğini gösterir; 2026-10-24 güncel Mac OSi model digest'i veya RAM/disk/latency kanıtı değildir.

## Bağımsız üretici lisans referansları
- https://huggingface.co/Qwen/Qwen3-14B — Qwen/Qwen3-14B model kartı lisans alanı: apache-2.0.
- https://github.com/QwenLM/Qwen3 — Qwen3 üretici deposu, açık ağırlıklı modellerin Apache 2.0 lisanslı olduğunu bildiriyor.
- GitHub/Ollama qwen3:14b tag'inin exact installed manifest/model digest ve paketlenmiş LICENSE zinciri bu kaynaklardan otomatik doğrulanamaz.
- Lisans uyumu hükmü: UPSTREAM_APACHE_2_0_VERIFIED / DEPLOYED_QUANTIZATION_LICENSE_LINK_HOLD.

## G07 / G03 ölçülmesi gereken açık gerçek kanıtlar
1. Güncel OSi'den Ollama list/show model kimliği, tag, digest, quantization, exact license metadata.
2. Modelin eşleşen lisans metni ve kullanım şartı + dağıtım/attribution sorumlulukları.
3. Mevcut router'ın yalnız local zero-cost yürütmeye bağlı olduğunun güncel preflight ve gerçek response evidence'ı; tarihsel paid-route fail-closed kanıtı.
4. Mac M5 Pro 24 GB üzerinde tek gerçek model inference ile önce/sonra RAM kullanımı, çalışan model belleği, disk alanı/model dosyası boyutu, latency/tokens per second, işlevsel benchmark.
5. Reviewer ve owner/issuer yetkileri ayrı geçiş kapılarıdır.

## Kabul muhasebesi
- GH-09-C1: CI_RUNTIME_BENCHMARK=PASS (run 40013986474).
- GH-09-C2: HOLD — upstream lisans kaynağı bulundu; deployed exact artifact ve lisans eşleşmesi eksik.
- GH-09-C3: HOLD — tarihsel sıfır maliyetli yerel rota PASS; güncel tam ürün zorunlu ücretli API bağımlılığı ve model tedarik zinciri karşıt incelemesi gerekli.
- GH-09-C4: HOLD — güncel yerel gerçek RAM/disk/çıkarım ölçümleri gerekli.
- Sayaç değişmedi: 13/76 CI_EVIDENCED; OFFICIAL_ACCEPTANCE=0/19.
- Tek hedef: mevcut kaynak ve motoru koruyarak gereken somut kanıtları tamamlamak; GITHUB_VERIFIED_FINISH=HOLD.
