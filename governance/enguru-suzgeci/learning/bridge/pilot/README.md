# ENGÜRÜ Mühendislik Kası™ — Çift Yönlü Köprü V1 GitHub Pilot

**Kalıcı sabit hedef:** İki pilot düğüm ve tek canonical ENGÜRÜ yetki zinciri.

- GitHub düğümü: bu deponun yalnız `feat/enguru-mk-bridge-pilot-v1-20261024` inceleme dalı. `tools/enguru_mk_bridge_github_v1.py` gelen **gizlisiz sabit kod** olayını doğrular, `acks/mac/` teslim belgesi ve `streams/github/` ters yönlü test olayı üretir.
- Mac OSi düğümü: ayrı ZIPapp. `~/Enguru/Runtime/MacEngineer/state/mk-bridge/bridge.sqlite` SQLite WAL depo. Bağımsız uygulama kaynaklarına, DoneCheck ve owner imzalarına yazım 0.
- Ortak protokol: `enguru.mk.bridge-event/v1`, `enguru.mk.bridge-ack/v1`, `TASK_ID=ENGURU_MK_BRIDGE_PILOT_V1`. Olaylar yalnız `PUBLIC_SANITIZED` sabit teşhis kodu taşır. Ham Mac logları, dosyalar, şifreler ve özel repo bilgileri kamusal alana gönderilmez.
- GitHub workflow `.github/workflows/enguru-mk-bridge-pilot-v1.yml`: yalnız exact review branch owner push için yanıt işçisi. `GITHUB_TOKEN` yetkisi yalnız görevde yazma kapsamı; `main` üzerinde değişiklik ve programlanan periyodik iş 0.
- Mac için `--self-test → --bootstrap → --queue-demo → --sync → --sync → --inspect` sırası uygulanır. `--sync`, mevcut owner'a ait `ENGURU_MK_GITHUB_TOKEN` gerekir; token depolanmaz/raporlanmaz.
- `ACK=RECEIVED_ONLY`; kod icrası, kaynak doğruluğu veya resmî DoneCheck kabulü anlamına gelmez.
- Kullanıcının ayrı oturumlardaki Yönetim/İcra GitHub motorlarına müdahale yoktur. PR #212 ve #213 korunur; bu PR yalnız pilot aktarım köprüsüdür.

## Kabul sınırı
1. Yerel Python referans modeli: 58/58 × 3, 174/174 PASS; ayrı uçtan uca sahte GitHub taşıyıcısı testleri dahildir.
2. GitHub owner-sınırlı `push` workflow ve `pull_request` izolasyon CI: exact commit ile `completed/success`.
3. Mac OSi: SHA kilitli ZIP, gerçek `--bootstrap` SQLite, `--queue-demo`, outbound HTTPS sync, GitHub ACK/ters olay, yeniden `--sync` sonrası `pending=0` ve `inbox>=1`.
4. Çevrimdışı/kayıp ACK/replay/hash farkı: ayrı ve idempotent saha kanıtı.
5. Nihai köprü Verified Finish: mevcut DoneCheck ve Human Threshold otoritesinin izinli kabulü; GitHub CI yalnız teknik ön koşuldur.

**İnceleme hükmü:** İzole tasarım ve CI PASS; gerçek Mac OSi iki yönlü saha pilotu ve resmî bitiş ayrı HOLD.
