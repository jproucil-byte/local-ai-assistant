# Návrh místních modelů (16. 10. 2026)

Počítač: NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM (ověřeno přes nvidia-smi).
Gemma3:4b už funguje a zůstává výchozí. Doporučení níže jsou kandidáti k porovnání,
nikoliv výsledky měření na tomto počítači. Nové modely nejsou automaticky stažené.

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
Nové kandidáty je potřeba otestovat; současná Gemma zůstává ověřená záloha.

Oficiální zdroje pro schopnosti, varianty a aktuální velikosti:

- [Qwen3.5 4B](https://ollama.com/library/qwen3.5:4b)
- [Qwen3-VL 4B](https://ollama.com/library/qwen3-vl:4b)
- [Qwen3.5 2B](https://ollama.com/library/qwen3.5:2b)
- [Ministral 3 3B](https://ollama.com/library/ministral-3:3b)
