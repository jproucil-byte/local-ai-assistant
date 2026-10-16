# Návrh místních modelů (16. 10. 2026)

Počítač: NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM (ověřeno přes nvidia-smi).
Gemma3:4b už funguje a zůstává výchozí. Doporučení níže jsou kandidáti k porovnání,
nikoliv automatická záruka lepších výsledků. Gemma3:4b a Qwen3.5:4b jsou nyní
nainstalované a ověřené na českém textu i umělém obrázku. Ostatní kandidáti stažení nejsou.

| Model v Ollamě | Navrhované využití | Přibližná velikost ke stažení |
| --- | --- | --- |
| `qwen3.5:4b` | První kandidát pro univerzální chat a rozbor obrazovky | 4,0 GB |
| `qwen3-vl:4b` | Kandidát pro čtení textu, prvků UI a snímků aplikací | 3,3 GB |
| `qwen3.5:2b` | Menší varianta k porovnání odezvy při průběžném sledování | 3,1 GB |
| `ministral-3:3b` | Alternativní malý model pro obrázky a vícejazyčný chat | 3,0 GB |

Všechny uvedené varianty podporují obrazový vstup. Velikost stažení není spotřeba
VRAM: další paměť vyžaduje kontext a zpracování obrazu. Menší počet parametrů sám
o sobě nezaručuje rychlejší odezvu; liší se kvantizace i obrazový enkodér.
Na tomto stroji bych nejprve porovnal Qwen3.5 4B a Qwen3-VL 4B s fungující Gemmou
na stejných českých otázkách a snímcích. Nepřenáším rodinné benchmarky na konkrétní
malé varianty. Pro průběžné sledování zvolit model podle skutečně naměřené latence.

Instalace jednoho vybraného kandidáta v PowerShellu:

```powershell
ollama pull qwen3.5:4b
```

Potom v Settings vybrat stejný název a uložit. Návrhy v nabídce neznamenají, že
model už je nainstalovaný. Nainstalované modely vypíše `ollama list`.
Další kandidáty je potřeba otestovat; současná Gemma zůstává výchozí.

## Orientační porovnání na tomto počítači

Ověřeno 16. 10. 2026 přes místní Ollamu, kontext 4096 tokenů, stejný systémový
prompt jako v aplikaci, ne-streamovaná odpověď. Oba modely hlásily 100% GPU.
Měřen byl čas do celé odpovědi, nikoli pouze do prvního tokenu. Modely byly nejprve
zahřáté. Textový dotaz zněl: „Co znamená adresa 127.0.0.1? Odpověz česky nejvýše
dvěma krátkými větami.“ Obrazový vstup byl uměle vytvořený obrázek 640 × 320
s textem „Error 404: File not found“, bez snímání skutečné obrazovky.

| Model / režim | Text, dva pokusy | Obrázek, jeden pokus |
| --- | --- | --- |
| Gemma3 4B | 0,985 / 1,062 s | 1,588 s |
| Qwen3.5 4B, výchozí uvažování Ollamy | 26,497 / 24,442 s | 20,745 s |
| Qwen3.5 4B, uvažování vypnuté | 2,496 / 1,116 s | 0,591 s |

Jde o malý orientační test, nikoli benchmark kvality nebo zaručenou latenci.
Dotazy a obraz se opakovaly; model mohl využít cache. Režim bez uvažování byl
měřen po režimu s uvažováním, takže zejména časy obrázků nejsou nezávislé.
První zahřívací požadavek Gemmy trval 8,757 s (načtení 8,455 s); Qwenu 59,053 s
(načtení 12,303 s a následné uvažování). První odpověď po načtení se proto nedá
srovnávat s odpovědí již zahřátého modelu.

Oba modely rozpoznaly chybu 404 a odpovídaly česky. Z těchto jednoduchých úloh
nelze vyvodit, že Qwen je kvalitnější. Gemma je vhodná výchozí volba pro rychlé
odpovědi. Qwen je alternativou k praktickému porovnání na složitějších úlohách.
Lokálně stažený balíček Qwenu má 3,32 GB; velikosti katalogových tagů se mohou
měnit s aktualizacemi. Modelové soubory zůstávají mimo Git.

V aplikaci Settings nabízí **Extended reasoning (Qwen3.5)**. Standardně je vypnuté
(`think: false`); zapnutí může výrazně prodloužit odpověď. Nastavení platí pro
chat i průběžné rozbory obrazovky u modelů s názvem `qwen3.5` (včetně jiných
velikostí). Ostatní rodiny modelů používají své původní chování.

## Větší varianty

- [Qwen3.5 9B](https://ollama.com/library/qwen3.5:9b): aktuální katalogový balíček
  přibližně 7,6 GB. Kandidát pro větší model stejné rodiny.
- [Gemma 3 12B](https://ollama.com/library/gemma3:12b): přibližně 8,2 GB.
  Větší varianta známého modelu, rovněž s obrazovým vstupem.

Na 8 GB VRAM jde o náročnější kandidáty: velikost souborů není celá provozní
paměť. Kontext, obraz a ostatní grafické aplikace vyžadují další místo. Odhaduji
proto riziko částečného přesunu do systémové RAM a vyšší latence; bez lokálního
testu neslibuji rychlost ani plné umístění na GPU. Tyto větší modely stažené nejsou.

Oficiální zdroje pro schopnosti, varianty a aktuální velikosti:

- [Qwen3.5 4B](https://ollama.com/library/qwen3.5:4b)
- [Qwen3-VL 4B](https://ollama.com/library/qwen3-vl:4b)
- [Qwen3.5 2B](https://ollama.com/library/qwen3.5:2b)
- [Ministral 3 3B](https://ollama.com/library/ministral-3:3b)
- [Řízení uvažování v Ollamě](https://docs.ollama.com/capabilities/thinking)
