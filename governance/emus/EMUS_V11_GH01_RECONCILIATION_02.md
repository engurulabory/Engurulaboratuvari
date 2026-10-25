# EMÜS V1.1 — GH-01 İkinci Kaynak Uzlaştırması
Tarih: 2026-10-23
Hüküm: GH01_PARTIAL / GH02_HOLD / GH03_HOLD / GH04_HOLD / OSI_HOLD
İnceleme PR: #210, review/emus-v11-github-prep-20261023

## Yeni doğrulanan hakikatler
1. `engurulabory/enguru-mac-engineer` erişilebilir özel depodur, default branch `main`; erişilen en yakın commit `5432b9b135499cea18273c0e003877b864af92c6` (2026-09-22). Bunun cihazda çalışan ürünün yetkili HEAD'i olduğu henüz uzlaştırılmadı.
2. `shared_ai/working_memory.py` Git blob `17aad24301b92f7a686469d4fc8fd50094e8754a`: `PersistentWorkingMemory` mevcut görev kayıtlarını JSON dosyalarıyla, temp dosya + fsync + os.replace kullanarak saklıyor. SQLite temelli olduğu iddiası doğru değil.
3. `tools/package3_working_memory_donecheck.py` checkpoint sonrası restart/resume ve stale revision guard örneği içeriyor; EMÜS genel uçtan uca görev başarısı kanıtı değildir.
4. `evidence/MAC_ENGINEER_V07_A03_A04_ENGINEERING_2026-09-22.md` ve `WORKLIST.md` içinde v0.7 idempotency/tek-yazıcı testlerine ilişkin kayıtlar bulunuyor. Kaydedilen sayılar: 100 replay → 1 created/99 duplicate ve 16 contenders → 1 writer/15 WriterBusy. Bunlar önceki v0.7 kapsamının beyan ve kanıt referanslarıdır; yeni EMÜS çalışma motorunun testi olarak sayılamaz.
5. `governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md` gerçek yetki zincirini DoneCheck v1.2 ile Human Threshold™ arasında ayırıyor. İnceleme dalındaki belge bu yetkileri devralmaz.
6. Özel Mac Engineer deposunda `AGENTS.md` fetch denemesi 404; dosyanın bu yolda erişilebilir olduğu doğrulanmadı. Ana depo AGENTS.md ortak başlangıç kaynağıdır, ürünün canonical kabul kaynakları ayrıca çözülecek.

## Düzeltici yön
- K02 ve G02: Önce mevcut JSON tabanlı hafıza, v0.7 kalıcı kayıt, yan etki idempotency ve tek-yazıcı mekanizmalarını aynı kabul testlerinde eşleştir. SQLite yalnız gerçek kabul açığını daha yalın ve güvenilir biçimde çözdüğü kanıtlanırsa kullanılacak. Tek motor ve mevcut kanıtlı kazanımlar korunacak.
- K01: İcra adaptörünü seçmeden önce aktif Mac Engineer v0.8 gibi yeni cihaz/ürün kaynak iddialarını güncel yetkili kaynakla doğrula.
- K03: reviewer/issuer/owner grant ve resmî DoneCheck yetkisinin kaynağını ayrı doğrula.
- GH01 kapama şartı: Tüm G01–G10 ve K01–K03 için somut kaynak, SHA/commit, test, owner ve gerçek GAP_MATRIX hükmü; ardından GH02 kabul sözleşmesi.
- SHA ayrımı: Git blob SHA-1 kanıtları, V3 kilit dosyasındaki SHA-256 değeri yerine geçmez. V3 byte-level SHA-256 doğrulaması açık.

## Sonuç
GH-01'in kaynak doğrulama kapsamı genişledi ve K02 mimari varsayımı düzeltildi. Bu yazılı kayıt mühendislik inceleme kanıtıdır; bağımsız CI, owner kabulü, resmî Verified Finish veya Mac OSi hazır oluş belgesi değildir.
