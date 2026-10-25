# PiLive — tek ekran veri sınırı V1

Bu sözleşme dört ekranın görsel tasarımı veya kullanıcı estetik kabulü değildir. Mevcut Progress Core API'lerinin kaynaklı sonuçlarını tek doğrulanmış modelde taşır. Core, canonical writer, P01/P02/P06 ve Human Threshold yetkileri korunur.

## Kaynak ve model

`registry()` tek proje kümesi otoritesidir; Work Contract keşfi mevcut Core'da kalır. Her key için aynı Core'un `summarize()` ve `structural_verify()` sonucu okunur. Adaptör keşif, ilerleme kanıtlama veya resmî kabul üretmez. Envelope içindeki packageSourceCommit ve packageManifestSha256, kullanılan adaptörün exact kaynağını bağlar.

`enguru.pilive.core-portfolio/v1` her canonical key/projectId çiftini bir kez içerir. İki kimlik birbirine dönüştürülmez. Core kaynak kodu ve başlangıç pinleri doğrulanır; registry keşfindeki Work Contract/schema girdileri ve her projenin State/Worklist/Work Contract byte'ları okuma öncesi/sonrası SHA çerçevesine alınır. Yeni/silinmiş keşif girdisi, HEAD veya byte kayması modelin tamamını HOLD yapar. Git HEAD ile SHA gözlemi birlikte raporlanır; loose worktree byte'ları otomatik committed/temiz kabul edilmez. Çoklu dosya atomikliği iddia edilmez.

## Proje satırı

| Alan | Kaynak ve anlam |
|---|---|
| key / projectId | Core registry() çıktısı; tekil ve ayrı |
| done / total / percent | Qualified Core countedPass / summary.total; tip, aralık ve kanıt matematiği doğrulanır; eksik/çelişik durumda null (N/A) |
| activeItem / activePackage / nextAction | Aynı proje ve kaynak SHA'larına bağlı Core summary; yapı geçerliyken kanıtlı aktif odak korunur |
| status / reason | Veri doğrulama durumu; PASS_CORE_READ_ONLY resmî ürün kabulü değildir |
| canonicalFinish | Canonical summary'nin kaynak beyanı; ör. PASS/LOCKED; yeni yetki hükmü oluşturmaz |
| finish | Core'un hesapladığı finishState; teknik veri alanı |
| officialAcceptance / closed | Bu salt-okunur katmanda HOLD / false; owner kabulü varsayılmaz |

Bir proje timeout, bozuk JSON, erişilemeyen kaynak, yanlış sayaç, kimlik veya digest uyuşmazlığı yaşarsa o satır görünür HOLD/N/A kalır. Diğer projelerin geçerli sonuçları korunur. Eski cache veya kısmi sayaç bu boşluğu güncel veri gibi doldurmaz. Bilinmeyen dış fact veya duplicate canonical kimlik, global kapsam uyuşmazlığıdır ve tüm model HOLD olur.

Bu ayrım Core registry() otoritesinin geçerli bir küme döndürmesine bağlıdır. Core'un kendisi bir Work Contract veya eksik zorunlu keşif girdisi nedeniyle registry() üretemezse portföy global HOLD olur; adaptör yeni bir keşif veya eski cache kümesiyle bu otoritenin yerine geçmez. Ayrıntılı hata yalnız özel makbuzda korunur.

## Zaman ve sunum

`sourceReadAt` koleksiyon başlangıcındaki muhafazakâr kaynak gözlem zamanı; `sourceObservations[key].sourceReadAt` o projenin Core API okuması tamamlandığı andır. Bunlar ilerleme olay zamanı veya file mtime değildir. `adapterBuiltAt` ayrı; `uiRenderedAt=null` ve `uiPublication=NOT_EXECUTED` gerçek ekran bağlanana kadar korunur. Yaş sınırı caller'ın açık eşiğidir; stale durumunda STALE ve sourceAgeSeconds gösterilir. Projection digest zaman metadata'sını dışarıda bırakır; aynı kaynak/sonuç sabit sırayla aynı digest'i verir.

Genel Durum/Projeler modeldeki kaynaklı satırları tüketebilir. Şimdi ekranında projeler arası tek odak seçimi mevcut yetkili canonical odak kaynağına aittir; bu adaptör birden çok projenin aktif işinden yeni global öncelik üretmez. Beş alan sınıflaması ve nihai SwiftUI tasarımı kendi kabul sözleşmesindedir.

## Kabul sınırları

Native capture PASS, kaynak gözleminin tamamlandığını gösterir; tüm proje sayaçlarının PASS olduğu anlamına taşınmaz. qualifiedCounters ve sourceBoundObservations sayıları ayrı raporlanır. U01/U02/U03/U04/U05/U09/U10/U12 alt kanıtları bu veri sınırına bağlanır. U01–U12 tam kabulü, gerçek GUI/erişilebilirlik/performance, bağımsız inceleme ve kullanıcı kabulü açık kalır.

Kurulu V3.1 binary SHA, güncel swiftc sürümü ve codesign metadata/verify sonucu yalnız mevcut kurulum gözlemidir. Tarihsel source→build recipe→kullanılmış toolchain→signing dönüşümü→binary manifesti gelene kadar buildBinding HOLD; güncel toolchain sürümü tarihsel derleyici kanıtı sayılmaz.
