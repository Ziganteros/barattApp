# barattApp
web app sviluppata in python che consente agli utenti di offrire prodotti in cambio di altri

filosofia dietro l'app:
il baratto è una forma inefficiente di scambio di merci per diverse ragioni:
- prodotti con valori differenti non sono frazionabili
- non è detto che trovi nel mio vicinato qualcuno disposto a ricevere quello che offro
es. baratto tra bici e auto
non posso offrire una bicicletta in cambio dell'1% di una automobile
ne tantomeno sarà facile trovare qualcuno disposto a dare un'auto in cambio di 100 biciclette

Che senso ha quest'app?
Se ci spostiamo su un bacino di utenza molto grande potremmo aumentare le probabilità di trovare qualcuno disposto ad accettare il nostro scambio
O viceversa l'app potrebbe avere successo in un micromondo come quello universitario in cui gli studenti scambiano volentieri appunti o altro materiale
Un altro mondo in cui questo tipo di app può prendere piede è il collezionismo.
Infine un ultimo ambito di applicazione può essere l'artigianato hobbystico, i side hustle e tutti i lavori fatti non come entrata principale...
... in cui potrebbe avere senso evitare scambi di denaro complessi da conciliare con il proprio profilo contributivo ...
Se poi vi piace vendere in nero su Ebay fate pure.

E tu che ci guadagni?
ho imparato a usare flask per sviluppare questa app.
E poi l'app si basa su una serie di utenti che mettono per iscritto quali prodotti vorrebbero... 


La logica di funzionamento è la seguente:
- utente x fa log in e aggiunge prodotti che vorrebbe scambiare e una lista di prdotti che vorrebbe in cambio
- associa ad ogni prodotto offerto/desiderato una category
- cliccando sul prodotto vengono visualizzate le specifiche e in basso compaiono tutti i prodotti della stessa categoria offerti e desiedrati da altri utenti.
- si può quindi aprire la pagina di uno di questi prodotti e vedere chi lo ha aggiunto tra i suoi offerti/desiderati
- si può aprire il profilo di questo utente y e mandargli un messaggio per proporre lo scambio

Work In Progress

si può lanciare il file app.py in locale ma è necessario creare un db su mongo denominato barattApp_DB che contenga 3 collection:
- Users
- Products
- Messages
è poi necessario sostituire nel file app.py username e password per la connessione al DB

Sviluppi successivi:
- si potrebbe implementare un sistema di notifica per i nuovi messaggi non letti
- creare una sezione cerca sia per utenti che per prodotti
- fare migliorie varie ed eventuali alla grafica
- nella pagina profilo aggiungere foto, domicilio, descriviti, altre info e uno storico degli scambi... anche un sistema di rewarding
- al momento il deploy è fatto su render ma solo perchè è gratis

- gli scambi sono fortemente consigliati di persona, ma si può immaginare una specie di spedizione incorciata o una hub intermedio in cui entrambi gli agenti dello scambio inviano i loro prodotti
- valutare di sostituire mongo con altro DB (azure potrebbe avere senso se poi lo uso anche per il deploy)
- oppure provare ad appoggiarsi per deploy e db su AWS o Google
- refactoring dell'intera app con javascript ... (non so se lo farò mai)
