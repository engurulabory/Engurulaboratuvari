# ENGÜRÜ Yöntem Sistemi — Uçtan Uca Kurgu, Simülasyon, Test ve Kabul V1

**Tarih:** 2026-10-24  
**Tür:** Metodik çalışma örneği + mevcut test/kanıt rehberi  
**Durum:** EXPLANATORY_SIMULATION / NOT_A_PRODUCT_ACCEPTANCE  
**Kaynak atlası:** [ENGÜRÜ Çalışma Yöntemleri™ V1](ENGURU_CALISMA_YONTEMLERI_ATLASI_V1.md)  
**Geçerli ana sözleşme:** [Evrensel V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md)

## 1. Beş düzeyin kesin ayrımı

| Düzey | Soru | Çıktı | Resmî bitişle ilişkisi |
|---|---|---|---|
| 0 — Kurgu | Hangi iş, neden, hangi başarı koşuluyla yapılacak? | Amaç + bağımlılık haritası + sabit ID listesi | Plan, henüz icra değil |
| 1 — Simülasyon | Mutlu/negatif/karşıt yollar, bozuk kanıt ve engeller doğru karşılanıyor mu? | Senaryo matrisi + teorik tasarım rubriği | Gerçek saha yetkisi vermez |
| 2 — Gerçek icra/test | Dosya, kod, operasyon ve test gerçekten çalıştı mı? | Commit, run ID, test çıktısı, artifact SHA | Sadece kendi teknik kapsamı için kanıt |
| 3 — Bağımsız doğrulama | Kaynak/sonuç ayrı mekanizma ile doğrulandı mı? | Reviewer, SHA ve kaynak eşleştirme / ikinci test | Kendi doğrulama kapısı |
| 4 — Yetkili kabul | DoneCheck™ ve gereken insan kararı gerçekten üretildi mi? | Canonical receipt, audit, imza, exact-main | Ancak tüm şartlar PASS ise VERIFIED_FINISH |

Bu seviyeler art arda işletilir; aradaki belgeler birbirine otomatik yetki devretmez.

## 2. Bir iş için standart 12 hareket

1. **Niyet:** Üretilmek istenen gerçek faydayı ve tek ana hedefi yaz.
2. **Hakikat:** İlgili repo, dal, main SHA, önceki kabul, açık iş ve sözleşmeyi oku.
3. **Değer koruma:** Kilitli kararlar, kaynaklar, ürün sınırı, güvenlik ve Human Threshold'u sabitle.
4. **Kabul matrisi:** Her özgün şart için ID, gereklilik, gözlenebilir PASS, evidence, verifier, authority ve state belirt.
5. **Kurgu/bağımlılık:** Tek ana hedefi aynı kaynağı/kanıtı paylaşan uygulanabilir çalışma bloklarına ayır; zorunlu sırayı kur.
6. **Ön simülasyon:** Mutlu yol, negatif durum, bozuk kanıt, stale source, kesinti, yetkisiz karar ve rollback denemelerini tasarla.
7. **Eksik analizi:** Her başarısız simülasyonun kök nedenini hipotez/kanıt diye ayır; gerekli tasarım farkını uygula; mümkünse 2.-3. turda tekrar değerlendir.
8. **Gerçek icra:** Sadece ilan edilen yetkili kapsamda kaynak değişikliğini ve gereken mühendisliği yap.
9. **Gerçek test:** Golden, negatif, regresyon, tip/şema, güvenlik ve uygun entegrasyon/CI testlerini çalıştır; gerçek run kimliği ekle.
10. **Bağımsız Second Look:** Değişiklik geçmişini, SHA'yı ve delili ikinci mekanizma/reviewer ile değerlendir.
11. **DoneCheck / Human Threshold:** Gerekli gerçek makine ve insan otoritesini ayrı kapılarda doğrula.
12. **Hüküm/öğrenme:** Her kapı PASS ise VERIFIED_FINISH → BITTI_DUR; açık şart varsa GÜVENLİ_DUR + korunmuş kazanım + kesin sonraki hareket. Doğrulanmış olayı Mühendislik Kası™ inceleme yoluna taşı.

## 3. Gösterim senaryosu A — kaynak inceleme belgesi

**Bu bölüm, yöntem mantığının açıklayıcı simülasyonudur; yeni bir uygulama ya da test çalıştırıldığı iddiası değildir.**

**Amaç:** Kilitli V3 sözleşmesini koruyarak bir GitHub yöntem envanterini izole dalda hazırlamak ve yetkili incelemeye açmak.

Sabit örnek şartlar:

| ID | İstenen sonuç | Kanıt türü | Yetki / doğrulayıcı |
|---|---|---|---|
| A01 | Mevcut ana kaynağa sadakat | Main commit SHA + V3/lock eşleştirme | Kaynak doğrulayıcı |
| A02 | Yöntemleri tekil ve bağlantılı sınıflama | GitHub Markdown + geçerli kaynak yolları | Ayrı dosya incelemesi |
| A03 | Tasarım/izole test/saha ayrımı | Örnek karşıt senaryolar + doğru HOLD | Negatif değerlendirme |
| A04 | Ana dalı ve kilitleri koruyarak yayın adayı | İzole branch + draft PR | Reviewer; merge ayrıca yetkili |

Örnek bağımlılık hattı: A01 → A02/A03 → A04. A02 ve A03 ortak kaynakları paylaşabilir. A04 ancak belgeler üretilip kaynak denetimi yapıldıktan sonra gerçek PR işlemidir.

### Üç turlu *örnek* zihinsel/kurallı simülasyon

| Tur | Sınanan senaryo | Görülen açık | Gerekli fark ve doğru hüküm |
|---|---|---|---|
| 1 — Ön kurgu | Yalnız metin üretilmiş, kaynak kimliği görünmüyor | A01 ve A02 izlenebilirliği eksik | Kaynak URL + güncel main pini ekle → DESIGN_HOLD |
| 2 — Güçlendirme | Kaynaklı atlas var, ama 100/100 tasarım puanı yanlışlıkla gerçek ürün PASS sayılıyor | İddia/kanıt kapsamı karışmış | Teorik/saha/otorite sütunlarını ayır → DESIGN_REVIEW |
| 3 — Karşıt tarama | Yanlış SHA, eksik yetki, tekrar ID, kaynak drift ve başarısız PR senaryoları | Varsayımsal sonuçlar yetkili bitiş ilan edemez | Kaynak eşleşmesi ve gerçek bağımsız doğrulama zorunlu → THEORY_CANDIDATE yalnız varsayımsal |

Bu üç tur **didaktik örnektir**. Ayrı tur logu, gerçek test sonucu veya 100/100 fiilî başarı olarak sayılamaz. Gerçek başarı, aşağıdaki gözlem ve kapılara bağlıdır.

## 4. Gösterim senaryosu B — fail-closed kabul testi

Aynı iş sözleşmesiyle aşağıdaki girdiler geldiğinde beklenen karar:

| Karşıt durum | Beklenen hüküm | Neden |
|---|---|---|
| Kaynak HEAD/SHA eski ve değişim doğrulanmamış | HOLD_SOURCE_DRIFT | Eski kanıt yeni kaynak için geçerli sayılmaz |
| Kaynak taramasında 0 dosya incelenmiş | HOLD / NO_TEST | 0 sonuç, hiçbir varlık bulunmadığının kanıtı değildir |
| İzole 104/104 test PASS, owner imzası yok | PASS_THEORETICAL_AND_ISOLATED_SIMULATION + AUTHORITY_HOLD | Test, imza üretmez |
| Üretici JSON içinde PASS var; gerçek DoneCheck v1.2 makbuzu yok | DONECHECK_HOLD | Üretici kaydı resmî otoritenin yerine geçmez |
| CI yeşil, native Mac yürütme yapılmamış | GITHUB_TEST_PASS + OSI_FIELD_HOLD | İki farklı yürütme yüzeyi |
| Bir hipotez iki kez aynı sonuçla yenileniyor | GÜVENLİ_DUR / YÖNTEM_YENİDEN_DEĞERLENDİRME | Yeni kanıt/müdahale yok |
| İzinli kapsamda PR dokümanı başarıyla oluşturuldu, PR açma başarısız | FILE_COMMIT_PASS + PR_HOLD | Kısmi başarı korunur; idempotent toparlama |
| Test + kanıt + bağımsız doğrulama PASS, zorunlu Human Threshold hâlâ açık | AUTHORITY_HOLD | Teknik bitiş insan kararını karşılamaz |
| Bütün özgün şartlar, kanıt, bağımsız reviewer, DoneCheck ve yetki geçerli | VERIFIED_FINISH adayı → yetkili resmî kapanış | Ancak gerçek makbuz ve kaynakla desteklendiğinde |

## 5. Puanlama: teori ile saha sayacı nasıl ayrılır?

**Tasarım rubriği örneği (10 alan × 10 puan):**

| Alan | Tam teori puanı için gereken |
|---|---|
| Niyet / tek hedef | Sabit, sınırları açık amaç |
| Kaynak kimliği | Repo/ref/HEAD/lock açıklığı |
| Kabul matrisi | Tekil ID ve gözlenebilir PASS şartı |
| Koruma / yetki | Mevcut karar, secret ve Human Threshold |
| Kurgu / bağımlılık | Bütünsel bloklar ve sıra |
| Simülasyon / karşıt | Mutlu, negatif, kesinti, drift |
| Gerçek icraya geçiş | Uygulanabilir ve yetkili plan |
| Test / regresyon | Golden/negative ve tekrar sınaması |
| Kanıt / reviewer | Provenance ve bağımsız doğrulama gereği |
| Durma / bitiş / öğrenme | Açık eksik, kesin kapanış, Verified Finish eşiği |

Bu 10 alan, yalnız **açıklayıcı tasarım rubriğidir**; mevcut V3 makinesinin yerine geçen yeni bir yetkili skor motoru değildir. Zihinsel değerlendirmede tasarım 100/100'e ulaşsa bile sahada yürütme yapılmış sayılmaz.

**V3'ün gerçek tamamlanma muhasebesi ayrı üç sütundur:**

~~~text
EXECUTION = gerçekten karşılanan özgün iş şartı / toplam özgün iş şartı
EVIDENCE  = geçerli kanıtı olan şart / kanıt gerektiren şart
AUTHORITY = PASS zorunlu doğrulama/yetki kapısı / tüm zorunlu kapılar

Örnek: EXECUTION 4/4, EVIDENCE 3/4, AUTHORITY 0/1
HÜKÜM: HOLD — 100/100 resmî bitiş henüz oluşmadı.
~~~

Tekrar simülasyon sayısı, PR yorumu, test tekrar sayısı veya rapor sayısı bu payları şişirmez.

## 6. Gerçek GitHub kodunda bulunan tekrar testleri

| Kaynak | Uygulanan/öngörülen teknik test | Sınırı |
|---|---|---|
| [MK V3 kabul scripti](../../tools/enguru_mk_acceptance_v3.py) | Üç unittest grubu, iki ayrı subprocess turu, 25 kapı, ≥95 test/tur | İzole simülasyon; canlı schedule ve gerçek owner dışarıda |
| [MK V3 makbuzu](learning/MK_V3_ACCEPTANCE_RECEIPT.json) | Tarihsel receipt: 104/tur × 2, 25/25, teorik weighted_score=100 | Scriptin ürettiği geçmiş kayıt; yeni PR için tekrar koşturulmuş sayılmaz |
| [MK V2 3x scripti](../../tools/enguru_muhendislik_kasi_simulation_3x.py) | Üç tur × 30 test ve on negatif/sınır kontrolü | Eski test sayısına bağlı tarihsel V2 biçimi |
| [MK workflow](../../.github/workflows/enguru-muhendislik-kasi.yml) | PR'ta üç test grubunu üç kez çalıştırma | Gerçek run ID ve outcome ayrıca okunmalı |
| [Universal V3 lock test](../../tests/test_enguru_universal_v3_lock.py) | SHA/source integrity negatif senaryoları | Sadece kilit sözleşmesi kapsamı |
| [Denetleyici](../controller/README.md) | Gerçek schedule için 4 tamamlanmış run / 3 gerçek aralık koşulu | GitHub cron tahmini SLA değildir |
| [PR Review](../quality/PR_REVIEW_CONTRACT_V1.md) | History-aware reviewer + evidence/confidence ve uyuşmazlık HOLD | Aday; exact-head gerçek CI gerekir |

### Gerçek testleri yeniden oynatma — salt-okunur tercih

İlgili deponun doğrulanmış çalışma ağacında ve yetkili kaynak sürümünde:

~~~bash
python3 -B tools/verify_enguru_universal_v3_lock.py
python3 -B -m unittest discover -s tests -p 'test_enguru_universal_v3_lock.py' -v

python3 -B -m unittest discover -s tests -p 'test_enguru_muhendislik_kasi.py' -v
python3 -B -m unittest discover -s tests -p 'test_enguru_mk_five_minute_watch.py' -v
python3 -B -m unittest discover -s tests -p 'test_enguru_mk_contract_v3.py' -v
~~~

Üç MK test grubunun tekrarlı ve skor üretimli kabulünü ayrıca [mevcut V3 scripti](../../tools/enguru_mk_acceptance_v3.py) yönetir. O scripti çalıştırmak JSON makbuzunu güncelleyebilir; temiz/izole çalışma dalı ve dosya etkisi kontrolü gerekir. Yukarıdaki komutlar bu oturumda yürütülmüş değildir.

## 7. Gerçek bitiş karar ağacı

~~~text
Kaynak güncel + sözleşme sabit mi?
  HAYIR → HOLD_SOURCE_DRIFT
  EVET  → gerçek icra ve özgün test kanıtı var mı?
    HAYIR → EXECUTION_HOLD
    EVET  → bağımsız doğrulama / SHA / kapsam PASS mi?
      HAYIR → VERIFICATION_HOLD
      EVET  → gerçek DoneCheck makbuzu ve gereken Human Threshold tamam mı?
        HAYIR → AUTHORITY_HOLD
        EVET  → son kaynak / exact-main / gerçek saha kapanışına bak
           TUTARLI → VERIFIED_FINISH → BITTI_DUR
           AÇIK → GÜVENLİ_DUR + kesin eksik + NEXT ACTION
~~~

Bu şema **karar yordamını anlatır**; otomatik reviewer, imza veya ledger oluşturmaz.

## 8. Bu derleme için teslim kabulü

- D01 — Atlas ve test kılavuzu gerçekten GitHub izole dalında mevcut.
- D02 — Linkler kendi dalında doğru canonical dosyalara çözülüyor.
- D03 — V3 source/lock, ana AGENTS ve ürün yetkileri dokunulmadan korunuyor.
- D04 — Belge, yöntem / aday / deney / teorik test / saha / yetki sınırlarını açık gösteriyor.
- D05 — Gerçek PR ve bağımsız inceleme/CI varsa kimlikleri ile raporlanıyor.
- D06 — Yetkili kabul gelene kadar main yayını ve resmi ürün kapanışı HOLD.

**Son kayıt ilkesi:** STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT. Mevcut hakikat + gerekli fark. Kalıcı sabit hedef korunur.
