# Control

Cartella per segnali di controllo degli scambi tra agenti.

Convenzioni suggerite:

- creare `STOP` per fermare tutti gli scambi;
- creare `PAUSE` per sospendere temporaneamente;
- rimuovere i segnali solo con decisione esplicita.

I task/agenti devono controllare questa cartella prima di processare una inbox.
