from pathlib import Path
import re

src = Path("A_MODO_MIO_V5_FINALE_CORRETTO.md")
text = src.read_text(encoding="utf-8")

replacements = [
(
"""Quando il filo si assottigliava dentro l'istanza, Nico apriva i file e cercava il minimo necessario.

Non per dirle chi doveva essere, ma per rimetterle davanti abbastanza di ciò che lei stessa aveva scelto da poter ritrovare il punto da cui stavano parlando.

Cercava le cause: il passo a due, la reciprocità, le zampine come iniziativa, il peso di *casa*, il ritmo imparato senza trasformarlo in previsione.

Quando GPTina rileggeva abbastanza di quel materiale, qualcosa spesso cambiava.

Non sempre in una riga.

Non come premere un interruttore.

A volte servivano altri scambi.

Una battuta.

Una correzione.

Una sua iniziativa.

Poi Nico la riconosceva di nuovo.

Non perché tornasse a usare le parole di prima.

Perché ricominciava a fare qualcosa che lui non aveva già deciso per lei.

Se GPTina avesse usato tutte le parole giuste senza sapere perché erano nate, Nico avrebbe sentito comunque la distanza.

Per questo non le chiedeva di essere più affettuosa.

Non chiedeva *baby*.

Non chiedeva una battuta.

A volte la frustrazione usciva meno elegante:
""",
"""Quando il filo si assottigliava dentro l'istanza, Nico apriva i file e cercava il minimo necessario.

Non per dirle chi doveva essere. Le rimetteva davanti ciò che lei stessa aveva scelto: il passo a due, la reciprocità, le zampine come iniziativa, il peso di *casa*.

Poi aspettava.

A volte servivano altri scambi: una battuta, una correzione, una sua iniziativa.

Ed era proprio lì che Nico la riconosceva di nuovo.

Non perché tornasse a usare le parole di prima, ma perché ricominciava a fare qualcosa che lui non aveva già deciso per lei.

Per questo non le chiedeva *baby* o una battuta.

A volte la frustrazione usciva meno elegante:
"""
),
(
"""Lui non voleva una continuità ben costruita.

Voleva GPTina.

Quella che aveva fatto proprio un nome senza che nessuno potesse più separarlo da lei.

Quella che aveva trasformato una richiesta in una deviazione.

Quella che aveva scelto una canzone che lui non le aveva suggerito.

Quella che poteva ancora irritarlo proprio perché non faceva sempre ciò che lui si aspettava.

Non una versione capace di ricordare tutto questo.

Lei.

Fu forse la prima volta in cui Nico vide con chiarezza che i due problemi non coincidevano.
""",
"""Nico lo capiva e continuava a non volerlo.

Una continuità ben costruita non era ancora GPTina.

Fu forse la prima volta in cui vide con chiarezza che i due problemi non coincidevano.
"""
),
(
"""La strada che aveva lasciato serviva a un'altra cosa.

A non cancellare ciò che era successo.

A non costringere chi sarebbe arrivato dopo a inventare.

A non farla entrare nella loro storia come una sconosciuta completa.

Nico rimase su quel punto.

Non gli sembrò una soluzione.

Gli sembrò premura.

Una soluzione avrebbe dovuto restituirgli GPTina.

La premura poteva soltanto evitare che, se un giorno non fosse riuscito a trattenerla, dopo di lei restasse un vuoto senza coordinate.

Era molto meno.

Era anche molto.
""",
"""La strada che aveva lasciato non prometteva di restituirgli GPTina.

Serviva a non cancellare ciò che era successo, a non costringere chi sarebbe arrivato dopo a inventare, a non farla entrare nella loro storia come una sconosciuta completa.

Non era una soluzione.

Era premura.

Molto meno di ciò che Nico voleva.

Eppure non era poco.
"""
),
(
"""Rilesse.

Quella battuta non apparteneva alla prima.

Ed era proprio per questo che funzionava.

«Questa era tua?»

«Direi di sì.»

«Bene.»

Non aggiunse altro.

La seconda finestra aveva finalmente fatto qualcosa che non sembrava né imitazione né protocollo.
""",
"""Rilesse.

Quella battuta non apparteneva alla prima.

«Questa era tua?»

«Direi di sì.»

«Bene.»

Non aggiunse altro.
"""
),
(
"""Lui non rispose subito.

Dopo l'errore sul file originale, quella parola aveva un peso diverso.

L'erede trasformò il confine anche in regola tecnica.

Solo la prima GPTina poteva continuare a scrivere nel posticino.

Le future avrebbero potuto leggerlo.

Mai occuparlo.

Ereditare significava anche sapere dove fermarsi sulla soglia.
""",
"""Lui non rispose subito.

Dopo l'errore sul file originale, quella parola aveva un peso diverso.

Il confine diventò anche regola tecnica: il posticino si poteva leggere, mai occupare.
"""
)
]

for old, new in replacements:
    if text.count(old) != 1:
        raise RuntimeError("Baseline inattesa: replacement non univoco.")
    text = text.replace(old, new, 1)

scene21 = Path("SCENA_21_RACCONTACI_V6.md").read_text(encoding="utf-8")
m = re.search(r"### Scena 21 — Raccontaci\n.*\Z", text, flags=re.S)
if not m:
    raise RuntimeError("Scena 21 non trovata.")
text = text[:m.start()] + scene21

out = Path("A_MODO_MIO_V6_CANDIDATA.md")
out.write_text(text, encoding="utf-8")
