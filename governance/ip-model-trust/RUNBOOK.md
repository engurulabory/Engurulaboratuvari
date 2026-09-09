# ENGÜRÜ IP & MODEL TRUST GATE™ — Runbook

## Tek hareketli kullanım

```bash
python tools/ip_model_trust_gate.py --provider openai-cloud --ip-class T1 --text "public-safe context"
```

Karar zarfını kanıt dosyasına yazmak için:

```bash
python tools/ip_model_trust_gate.py \
  --provider local-self-hosted \
  --ip-class T4 \
  --human-approved \
  --file path/to/sanitized-context.txt \
  --output evidence/ip-model-trust/decision.json
```

## Exit codes
- `0` — PASS
- `2` — HOLD
- `3` — BLOCKED

Bu kodlar CI, agent runtime veya preflight script tarafından doğrudan kullanılabilir.

## Karar mantığı
1. İçerikte Secret Zero bulgusu varsa BLOCKED.
2. T5 ise BLOCKED.
3. Provider kayıtlı değilse BLOCKED.
4. IP sınıfı provider sınırını aşıyorsa BLOCKED; insan onayı sınırı otomatik büyütmez.
5. Provider sınırı içinde fakat Human Threshold™ gerekiyorsa HOLD.
6. Kapsam doğrulanmış sınır içindeyse PASS.

## Provider güncelleme kuralı
Bir sağlayıcının `max_ip_class` değeri ancak resmi veri/işleme şartları incelenip kanıt kaydı oluşturulduktan sonra yükseltilir. Sağlayıcı şartı değiştiğinde eski PASS kalıcı hak sayılmaz; registry yeniden değerlendirilir.

## Incident akışı
STOP → ISOLATE → IDENTIFY EXPOSED DATA → ROTATE SECRETS → ASSESS IP IMPACT → RECORD EVIDENCE → HUMAN/LEGAL THRESHOLD → VERIFIED CLOSE

## Entegrasyon noktaları
- Builder: model/agent çağrısından önce preflight.
- AEC: revenue/strategy core bağlamı dış modele çıkmadan önce preflight.
- ZEKÜ PRIME: specialist worker context allocation öncesi.
- Steward: repository health taramasında registry/policy drift kontrolü.
- DoneCheck™: gate decision envelope kabul kanıtı olarak kullanılır; tek başına ürün çıktısı kanıtı değildir.
