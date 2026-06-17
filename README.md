# Sayısal Tasarım Mantık Devresi Simülatörü

Bu proje, Sayısal Tasarım dersi kapsamında hazırlanmış basit bir **mantık devresi simülatörüdür**. Uygulama Python ve Tkinter kullanılarak geliştirilmiştir. Kullanıcı arayüzü üzerinden giriş elemanları, çıkış elemanları ve temel mantık kapıları oluşturulabilir; bağlantılar kurularak devre çıktıları simüle edilebilir.

Projede ayrıca özel bir uygulama ikonu bulunur. Bu ikon hem Tkinter penceresinde kullanılır hem de PyInstaller ile `.exe` oluşturulurken çalıştırılabilir dosyanın simgesi olarak ayarlanabilir.

## Özellikler

* AND, OR, NOT, BUFFER, NAND, NOR, XOR ve XNOR kapıları
* Giriş kutusu oluşturma ve giriş değerini değiştirme
* Çıkış kutusu ile sonucu görüntüleme
* Canvas üzerinde eleman yerleştirme
* Elemanlar arasında bağlantı kurma
* Kapı çıkışlarını hesaplama
* Harici kapı görseli gerektirmeyen çizim tabanlı Tkinter arayüzü
* Tkinter pencere ikonu ve EXE ikonu için hazır `app_icon.ico`
* Test edilebilir modüler mantık motoru

## Proje Yapısı

```text
sayisal-tasarim-mantik-devresi-simulatoru/
├── README.md
├── pyproject.toml
├── .gitignore
├── src/
│   └── sayisal_tasarim_simulatoru/
│       ├── __init__.py
│       ├── logic.py
│       ├── gui.py
│       ├── main.py
│       └── assets/
│           ├── app_icon.ico
│           └── app_icon.png
└── tests/
    └── test_logic.py
```

## Kurulum

Python 3.10 veya üzeri önerilir.

```bash
python -m pip install -e .
```

Bu proje yalnızca Python standart kütüphanesini kullanır. Tkinter çoğu Python kurulumunda hazır gelir.

## Çalıştırma

```bash
python -m sayisal_tasarim_simulatoru.main
```

veya paket kurulumundan sonra:

```bash
sayisal-tasarim-simulatoru
```

## Kullanım

1. Üst menüden bir araç seçilir.
2. Canvas üzerine tıklanarak giriş, çıkış veya kapı eklenir.
3. **Connect** aracı seçilerek önce kaynak elemana, sonra hedef elemana tıklanır.
4. Input elemanlarına çift tıklanarak giriş değeri 0/1 olarak değiştirilir.
5. **Run** butonu ile devre çalıştırılır.
6. **Reset** butonu ile devre temizlenir.

## Mantık Kapıları

| Kapı   | Açıklama                                 |
| ------ | ---------------------------------------- |
| AND    | Tüm girişler 1 ise 1 üretir.             |
| OR     | En az bir giriş 1 ise 1 üretir.          |
| NOT    | Tek girişi tersler.                      |
| BUFFER | Giriş değerini aynen aktarır.            |
| NAND   | AND sonucunun tersini üretir.            |
| NOR    | OR sonucunun tersini üretir.             |
| XOR    | Girişlerden tek sayıda 1 varsa 1 üretir. |
| XNOR   | XOR sonucunun tersini üretir.            |

## Testler

```bash
python -m unittest discover -s tests -v
```

## Windows EXE Oluşturma

Windows kullanıcıları için uygulama PyInstaller ile tek dosyalık `.exe` hâline getirilebilir.

Önce PyInstaller kurulur:

```bash
python -m pip install pyinstaller
```

Ardından proje ana klasöründe şu komut çalıştırılır:

```bash
pyinstaller --onefile --windowed --name sayisal-tasarim-simulatoru --icon src\sayisal_tasarim_simulatoru\assets\app_icon.ico --add-data "src\sayisal_tasarim_simulatoru\assets;assets" src\sayisal_tasarim_simulatoru\main.py
```

Oluşan dosya şu konumda yer alır:

```text
dist/sayisal-tasarim-simulatoru.exe
```

Bu komutta:

* `--onefile` tek bir `.exe` dosyası üretir.
* `--windowed` çalışırken ek komut satırı penceresi açılmasını engeller.
* `--icon` EXE dosyasının simgesini ayarlar.
* `--add-data` ikon dosyalarının EXE içine eklenmesini sağlar.

## Geliştirme Notları

Önceki tek dosyalı yapı yerine mantık hesaplama bölümü ve arayüz bölümü ayrılmıştır. Böylece mantık kapıları GUI olmadan test edilebilir, arayüz ise ayrı olarak geliştirilebilir.

## Hazırlayan

* Gürel Bilgin