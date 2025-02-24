#%%
import twitter_tools_v2 as tt
import pandas as pd
import prousuario_tools as pt

#%%


def add_to_neutral(word):
    if word not in NEUTRAL_STRINGS:
        print(f'{word} agregada')
        return ''.join([NEUTRAL_STRINGS, f'|{word}'])
    else:
        print(f'{word} ya esta en NEUTRAL STRINGS')


def thanker(df):
    # for f in list(BANK_USERS.keys()):
    filtro = df.text.str.lower().str.contains('gracias')
    df.loc[filtro, 'positivo'] = 1
    for i in df.loc[filtro].index:
        if df.loc[i, 'negativo'] == -1:
            df.loc[i, 'positivo'] == 0
    return df

def assign_sentiments(df):
    df['negativo'] = df.text.str.contains(NEGATIVE_STRING).astype(int).copy()
    df['positivo'] = df.text.str.contains(POSITIVE_STRINGS).astype(int).copy()
    df.loc[df.text.str.contains(NEUTRAL_STRINGS), ['positivo', 'negativo']] = 0
    return df


def sum_sentiment(df):
    bank_feeling = {}
    for b in BANK_USERS:
        bank = BANK_USERS[b]
        filtro = df.text.str.contains(b)
        feeling_sum = df[filtro].sentimiento.sum()
        tweet_count = df[filtro].sentimiento.count()
        if bank not in bank_feeling:
            bank_feeling[bank] = {
                'feeling':feeling_sum,
                'count':tweet_count
                }
        else:
            bank_feeling[bank]['feeling'] += feeling_sum
            bank_feeling[bank]['count'] += tweet_count
    bank_feeling = pd.DataFrame(bank_feeling).transpose()
    return bank_feeling

def sum_sentiments(df):
    bank_feeling = {}
    rts = '|'.join(['rt @' + x for x in USERNAME_FILTER_STRING.split('|')])
    for b in BANK_USERS:
        bank = BANK_USERS[b]
        filtro = df.text.str.contains(b)
        no_rt_filtro = ~df.text.str.contains(rts)
        user_filtro = ~df.user_screen_name.str.lower().str.contains(USERNAME_FILTER_STRING)
        filtro_general = filtro & no_rt_filtro & user_filtro
        bank_df = df[filtro_general]
        positive_sum = bank_df.positivo.sum()
        negative_sum = bank_df.negativo.sum()
        tweet_count = filtro.sum()
        if bank not in bank_feeling:
            bank_feeling[bank] = {
                'positive':positive_sum,
                'negative':negative_sum,
                'count':tweet_count
                }
        else:
            bank_feeling[bank]['positive'] += positive_sum
            bank_feeling[bank]['negative'] += negative_sum
            bank_feeling[bank]['count'] += tweet_count
    bank_feeling = pd.DataFrame.from_dict(bank_feeling, orient='index')
    return bank_feeling

def calculate_feelings(df):
    df['negative'] = (
        (
            df['negative']
            .apply(abs)
            /df['count']
        )
        .fillna(0).round(2)
    )
    df['positive'] = (
        (
            df['positive']
            .apply(abs)
            /df['count']
        )
        .fillna(0).round(2)
    )
    df['neutral'] = (1 - (df['positive'] + df['negative'].abs())).round(2)
    df.sort_values('count', ascending=False, inplace=True)
    # feels['negative'] = feels['negative'].apply(lambda x: f'{x:.2f} %')
    # )
    return df[['count', 'positive', 'neutral', 'negative']]

def calculate_feelings2(df):
    count = df['count']
    positive = df['positive'].abs() / count.fillna(1)
    negative = df['negative'].abs() / count.fillna(1)
    neutral = 1 - (positive + negative)
    df = df.assign(
        count=count,
        positive=positive.round(2),
        negative=negative.round(2),
        neutral=neutral.round(2)
    ).sort_values('count', ascending=False)
    return df[['count', 'positive', 'neutral', 'negative']]

def non_neutral(df):
    suma = df['positive'].abs() + df['negative'].abs()
    df['negative'] = (df.negative.abs()/suma).fillna(0)
    df['positive'] = (df.positive.abs()/suma).fillna(0)
    df.sort_values('count', ascending=False, inplace=True)
    return df[['count', 'positive', 'negative']]

def filter_users(x):
    return x not in USERNAME_FILTER_STRING

def main(tweets_bancos, filter=False):
    print('inicia proceso')
    if filter:
        filtro = tweets_bancos.user_screen_name.apply(filter_users)
        tweets_bancos = tweets_bancos[filtro]
    print('preparo data')
    # no_rts = tweets_bancos.text.str.startswith('rt')
    # tweets_bancos = tweets_bancos[~no_rts]
    raw_feelings = assign_sentiments(tweets_bancos)
    print('asigno sentimientos')
    sum_feelings = sum_sentiments(raw_feelings)
    print('sumo sentimientos')
    feelings = calculate_feelings(sum_feelings)
    feelings = feelings.drop('count', axis=1)
    print('calculo sentimientos')
    # feelings.to_excel(f'{FOLDER_NAME}bank_feelings_{CURRENT_MONTH}.xlsx')
    print('exporto archivo')
    return feelings, raw_feelings


NEGATIVE_STRING = (
    'usted|robo|abus|engaño|peor|relajo|estafa|ineficien'
    '|cansad|atropello|roba|burla|descar|timad|incapa|ladr'
    '|quej|insolit|fraude|presion|caso|irresp|respo|proconsumidor'
    '|oblig|inaudit|trampa|derecho|diablo|carajo|adrede'
    '|avergonz|atraso|ladron|boicot|corrupcion|joda'
    '|que harán con mi dinero|adrede|mala costumbre|avergonz'
    '|atraso|no contestaron|no son faciles|ladron|boicot'
    '|corrupci|no me hicieron caso|ellos son espectaculares'
    '|que se joda|no puedo|coño|que tiene el internet banking'
    '|aun nada|no responde|ojos abiertos|que presten atención'
    '|lamentamos los inconvenientes|diabluras|excusa que me dieron'
    '|me voy de este banco|hacerme perder|averia|avería'
    '|violando la norma|no le importan los clientes'
    '|dias esperando|días esperando|insorportable|😡'
    '|bárbaros|barbaros|aunque sea por cortesía|no saben dar respuesta'
    '|devuelvan nuestros ahorros|mal servicio|👎'
    '|agujero financiero|mala práctica|mala practica'
    '|peor en el mundo|reclamacion|reclamación|inaudito'
    '|quiero es respuesta|quiero respuesta|prousuario|abusivo'
    '|negocios con el estado|atencion|atención|como piensa el pueblo'
    '|muchas llamadas|no resolvio|no resolvió|evidenciar|🥚'
    '|atracador|maldit|🤡|cancele una tarjeta|duplicando los pagos'
    '|increíble|increible|cogiendo lucha|bloquearon mi cuenta'
    '|superdebancosrd|lucha que cogi|bodoficial|mala fama'
    '|dejen de llamar|inservible|nunca resuelven|maco'
    '|decepci|decepcionad|siguen cobrando|tendré que pagar'
    '|siguen haciendo lo mismo|devuelvan nuestros ahorros'
    '|peor|problemas con el servicio al cliente'
    '|no he recibido respuesta|🙃|siempre con problemas'
    '|no me gusta ese servicio|abusivo'
    '|no puedo con la aplicación del @popularatulado'
    '|un problema serio|nadie me resuelve'
    '|me parece discriminatorio|exponiendo mi correo'
    '|nadie sabe nada|halón de orejas|lejos del banco|oye esa vaina'
    '|rapa su madre|cada vez que llamo|penoso|ladron|mierda'
    '|revisar su politica|y esta es la fecha que no|fila de madre'
    '|alegando es|banco mas mediocre|cierro la cuenta|que abuso'
    '|no avisaron nada|no ha pasado nada|estoy esperando su respuesta'
    '|esperando que [a-z\\s]+ se refleje|es mejor seguir siendo arcaico'
    '|imaginate los privados|porqueria de sistema|no es justo'
    '|no devuelven el dinero|no es posible que|muy perdidos sus empleado'
    '|más de [0-9]+ meses cancelada|mi tiempo es gratis'
    '|no juegue con la inteligencia|si caminas frente a un popular, toma la otra acera'
    '|el error fue de ustedes|peor servicio|dias esperando'
    '|necesito que [a-z]+? resuelvan|es un abuso|servicio [tan]? pésimo'
    '|esa transferencia pasó a|duplicar el cargo|abusó'
    '|lo mejor que he hecho es llevarme mi vida del @popularenlinea'
    '|no me dieron razón|con el banco caribe mi error'
    '|tengo problemas con el punto de venta inalambrico'
    '|esa práctica me parece que es del popular'
    '|me llamaron 3 veces al teléfono que no es'
    '|en el @bhdleon son tan mierdas'
    '|agilizar el servicio al cliente'
    '|colapsado el sistema|me tienen un lio|son pésimo'
    '|me roban el dinero|mamense un guebo'
    '|se beneficia de mi dinero|pero ustedes están robando'
    '|el primer pago llegó, el segundo no'
    '|200 malditos pesos|maldita sea|me cobraron un maldito cargo'
    '|no está funcionando la plataforma|agente inepto'
    '|te están quitando ese día|no puedo acceder en ningún lado'
    '|dar la cara frente a estafas|buenos charlatanes'
    '|estaré cancelando tarjeta'
    '|quien protege al cliente'
    '|no puedo hacer transferencias'
    '|para cobrarme la tarjeta solían ser más diligentes'
    '|deberían ampliar sus respuestas'
    '|asociación popular me puso a dar vueltas un año'
    '|ganas de joder|y entonce?'
    '|en un grupo de personas de un lio hacer una consulta'
    '|el servicio más pésimo'
    '|tienen algo que aportar'
    '|respondan|hace casi una hora|que servicio tan terrible'
    '|🤦🏽‍♀️|los errores nunca son en beneficio de uno'
    '|a ver si dejan el relajo|victorvargas|victor vargas'
    '|son unos rsmm|no me dan respuesta|qué lío con estos bancos'
    '|devuelvan nuestros ahorro|travesía con el @bhdleon'
    '|me tienen jalto|robando|error de ustedes|perder [0-9]? horas de mi vida'
    '|una pupu de banco|me tiene jarta|a joder a un banco'
    '|transferencia no aparece|va a quebrar|nunca te los devolverán'
    '|nunca reconoce al cliente|muy atinada la aplicacion'
    '|cayó la plataforma|@luisabinader @bancamerica|un maldito abuso'
    '|responde mi dm|los sistemas del @bhdleon están abajo'
    '|@bodoficiai|grupo bod|tengo 1 semana esperando|toy harto'
    '|llamando para ofrecer tarjetas|tuve que pagar de nuevo|no cayo el dinero'
    'devolverme mi dinero|tengo préstamos aprobados|#bodelorigendelaestafa'
    '|toyosos|no hay plástico|he tratado de usar mi tarjeta y no he podido'
    '|cual es la finalidad del chat|carta de saldo cuesta'
    '|duplica un cargo|me cobran mora|fuck|lamentablemente|no saben explicar'
    '|aleja [más]? a sus clientes|no hay un cajero|que sirva o tenga dinero'
    '|cumplan con la ley|artimañas|lento|app no está funcionando'
    '|experiencias típicas del @scotiabankrd|no hacen nada'
    '|por quinta vez les explico|42 días esperando|estafado|estafadores'
    '|los bancos cobran hasta la respiración|esta situación en la sucursal'
    '|me tienen hart|se demoraron una eternidad'
    '|no se puede agregar un beneficiario|no puedo resetear mi usuario'
    '|ganancias excesivas|a quién del @scotiabankrd se le ocurrió'
    '|sigue igual de deficiente|para no resolver|2 años sin ir al'
    '|como es posible que|nadie da respuesta|segunda reclamación'
    '|el @bhdleon ‘ta igual que el popular|la mala soy yo'
    '|cerrado aun|lo poco que sirven sus cajeros|arréglenlos'
    '|el @banreservasrd me roba|aun no cae el dinero'
    '|bajen el costo de transferencia'
    '|los cajeros del @banreservasrd|no tienen dinero y están dañados'
    '|un robo|no se que mas decirle|malas experiencias'
    '|hacer una fila|tendré que retirar mi cuenta'
    '|es indignante|no se puede acceder|q chistazo|son unos abusadores'
    '|no me podía reembolsa|siempre tienen una maldita excusa'
    '|no me interesa ser su cliente|elimínenme de su base de datos'
    '|servicio al cliente es pena que da|tú ves las oficinas full con cosas'
    '|mala fe|el delincuente @popularatulado|sin funcionar el app'
    '|el cajero se friso|nadie me dice nada|atosigadores'
    '|no puedo agregar un beneficiario|la web tampoco me lo permite'
    '|hay que irle sacando pies|están cobrando 300 cosas que no tienen sentido'
    '|banda de clonadores chipero|seamos más serios|me niegan el reclamo'
    '|tuve muchos temas con ellos|no me aceptó reclamación'
    '|necesito respuesta|consumo que jamas realicé|@bhdleon no te da un estado de cuenta'
    '|ustedes me acaban de coger|transferencia interbancaria hace 3 horas'
    '|me cobran 100 pesos|nada de resolver|nada de respuesta|su gerente'
    '|no veo seriedad|no estan supuestos a llamarte|mejorar el servicio al cliente'
    '|no honró el descuento publicado en la aplicación|insólito'
    '|imposible comunicarse con el servicio al cliente'
    '|entidad financiera puede llamar a usuario próximo a 7'
    '|eso no lo coge el cajero|cargos generados|no me da respuesta'
    '|que huevo puso el @bhdleon|ineficientes|banreservas se lo roba'
    '|la @superdebancosrd no regula los bloqueos'
    '|cajero del @bhdleon que funcione|la mafia que opera'
    '|tienes dos meses con una cuenta|los cajeros se tragan las tarjetas'
    '|no hay tarjetas de debito disponibles|por parte he visto publicación'
    '|como diablos uno encuentra el horario|30 pesos de comisión por una transacción'
    '|me robaron|nunca el cajero me dio|tiene una avería|solucionen eso rapido'
    '|no puedo entrar a la app|da error|malditos ineptos|no hacen nada'
    '|ni actualiza los precios|tengo problemas|otra vez tengo problemas'
    '|problemas con su app|jarta de poner reportes|qué pasa con su plataforma'
    '|por lenta|pésimo servicio al cliente|arreglar la plataforma'
    '|no me han dicho nada|que mal servicio|me tienen sin un peso'
    '|increíble lo del|se quedan se quedan en espera|3 semanas con mi tarjeta'
    '|sin funcionar la aplicacion|serian el mejor banco|con ustedes no dan ganas'
    '|si me lo descontaron|app me da error|sin sistema|la real ineficiencia'
    '|nadie atendió la situación|lo único que hicieron|los prestamistas'
    '|me robó|un abuso|sinvergüenzas|rechaza todas las reclamaciones'
    '|me da un error|su plataforma tiene problemas|está muy lenta'
    '|app no me deja registrarme|el cajero no lo acepta'
    )

POSITIVE_STRINGS = (
    'excelente|buen trabajo|atenciones|mis bancos si|mejor banco'
    '|disponible para todos los usuarios|buen banco|complacid'
    '|muy bien|premio mujeres|agradezco|buen trato|vocaci'
    '|ser ejemplo|hermoso mensaje|ternura|bonito|😀|❤'
    '|excelencia|dedicac|🤩|hermosa|excelente ejemplo|inclusion'
    '|resolvio|resolvió|situación que estamos viviendo|sostenibilidad'
    '|buenas practicas|buenas prácticas|👏|si son justos'
    '|igualdad de género|que bien que te resolvieron|excelente la atención'
    '|todo salió bien|estoy muy conforme'
    '|nadie se le acerca al apap|💞|🙏|representantes competentes'
    '|gracias por su respuesta|el mejor producto|encantado!|me encanto'
    '|el servicio ha mejorado bastante|su app para mi es la mejor'
    '|el mejor banco|@banreservasrd que alegría|mejor sucursal|buen trato'
)

NEUTRAL_STRINGS = (
    '@elreydelaradio|serie del caribe|campeon|aguilascibaenas'
    '|#lidom|@lidomrd|nuestros jugadores|vuelta ciclista independencia'
    '|elreydelaradio|escogidistas|cervpresidente|sussydeportes'
    '|tenchyrodnyc|ronbrugal|campeonato|fiba|semifinaldgt2'
    '|independencia|fiestas patrias|#seriedelcariberd|seriecaribe2021'
    '|fedombal|padre de la patria|díadelamujer|díainternacionaldelamujer'
    '|afp|itobisono|RDBSeleccion|idacrd|rt @santiagohazim|rt @diputadosrd'
    '|oferta valida|rt @danilopaulinor|@diputadosrd|vacunaterd'
    '|temporada|mlbdominicana|rt @spereyrarojas|beisbol'
    '|informe de sostenibilidad|gran prix internacional|rt luisminoso'
    '|deporte|vacunarte|remolcadas|jonron|home-run|home run'
    '|rt @popularenlinea|rt @popularatulado|rt @banreservasrd|rt @scotiabankrd'
    '|rt @bhdleon|rt @bancobhdleon|rt @bsc_rd|rt @bancocariberd|rt @bancobdi'
    '|rt @bancovimenca|rt @bcolopezdeharo|rt @bancamerica|rt @promericard'
    '|rt @banescord|rt @bcolafiserd|rt @ademibanco|rt @bancoademi'
    '|rt @bellbankdr|rt @asocpopular|rt @acapdom|rt @asocperavia'
    '|rt @asocromana|rt @alaverrd|rt @asocduarte|rt @asomaprd'
    '|rt @asocmocana1|rt @abonap_|rt @asoclanacional|vacuna|jeanarodriguezs'
    '|aguilas|operacion medusa|jean alain rodriguez|politiquera|sonia mateo'
    '|rt @banreservasrd|rt @spereyrarojas|rt @carolinamejiag'
    '|rt @itobisono|rt @bsc_rd|rt @orlandojm|rt @lnbf_rd'
    '|rt @sbfernandezw|rt @popularenlinea|rt @gabrielmercedez'
    '|rt @asoclanacional|rt @felixportes|rt @despertarnacio2'
    '|rt @notidigitalrd1|rt @eddymontas|rt @aquilesjimenez'
    '|rt @danilopaulinor|rt @presidenciard'
    '|rt @rcavada|rt @lavozdelyaque'
    '|rt @alcaldiadn|rt @visaiberiablh|rt @diputadosrd'
    '|rt @fansreflexiones|copa @banreservasrd|luis pandora'
    '|#banreservasactivolapelota|rt @hgomez27|@lidomrd|rt @itobisono'
    '|gigantes del cibao|rt @despertarnacio2|rt @elreydelaradio|golfistas'
    '|tigresdellicey|yancenpujols|rt @ingcarcas1|vacuna|edwardchaa'
    '|rt @andresvander|rt @robertofulcar|corrupción|odebrecht'
    '|fiesta de[l]? @banreservasrd|peledeses|derroche con dinero del estado'
    '|#batalladelafe2022|cristiano|@unstoppable8672|rt @mirexrd'
    '|#xiipremioscorresponsables|rt @guerreromiguele|rt @diputadosrd'
    '|corrupcion|#fitur2022|fitur|licey|aguilas|rdbrillaenfitur'
    '|rt @luisabinader|rt @martepiantini|fideicomiso|misterdeportes'
    '|béisbol|faride|políticos dominicanos|@daris_sanchez'
    '|#expofomentapymesbanreservas|wendysantosb|#logrosdelcambio'
    '|chris duarte|por justificar el dinero que te pagan|aquamanrd'
    '|@c_duarte5|@tatis_jr|rt @anarossina|danilo medina|rt @presidenciard'
    '|@miculturard|excelente resultados a favor de samuel pereyra'
    '|#herencia rosario rd|@alcaldiadn|@davidortiz'
    '|las utilidades netas de @banreservasrd|rt @raquelarbaje'
    '|soy escogidista|rt @aquilesjimenez|#laselecciondelpueblo|#fibawc'
    '|rt @carlosgabrielgc|liga de béisbol profesional|ldfcomdo'
    '|rt @sanzlovaton|#bonoverde|rt @joeltorresdo|carrera 5k'
    '|dominicanosasimplevista|#enmariasela sería excelente un apoyo de parte'
    '|rt @sanzlovaton|baconator|rt @mlbdominicana|rt @danilopaulinor'
    '|#familiarosario|rt @pedrobotellord|afp|viva luis abinader'
    '|arriba samuel pereyra|#banreservaseldorado|#eldorado'
    '|samuel pereyra|baloncesto|rt @wendycuevas3|@leoneslistaprm'
    '|rt @fansreflexiones|luis abinader|rt @elnuevodiariord'
)

USERNAME_FILTER_STRING = (
    'popularenlinea|popularatulado|banreservasrd|scotiabankrd|bhdleon'
    '|bancobhdleon|bsc_rd|bancocariberd|bancobdi|bancovimenca|bcolopezdeharo'
    '|bancamerica|promericard|banescord|bcolafiserd|ademibanco|bancoademi'
    '|bellbankdr|asocpopular|acapdom|asocperavia|asocromana|alaverrd'
    '|asocduarte|asomaprd|asocmocana1|abonap_|asoclanacional|prousuariord'
    '|superdebancosrd|sbfernandez|fansvipfotocron|elnuevodiariord|listindiario'
    '|cdn37|z101digital|antena7oficial|diputadosrd|carolinamejiag|presidenciard'
    '|senadord|rodrigmarchena|agoramallrd|mananerord|elreydelaradio|super7fm'
    '|megacentrord|gloriareyesg|eduardoestrella|vicerdo|tusambildo|intrant_rd'
    '|rdbseleccion|mlbdominicana|miderec_rd|alcaldiadn|domexcourier|anoticias7'
    '|scotiabankhelps|estonoesradiotw|edesurrd|tpago|reconocidosnet'
    '|carlosgabrielgc|laurabonnellyv|visaiberiablh|spereyrarojas|condesatv1'
    '|lnbf_rd|itobisono|lidomrd|unstoppable8672|fuegoalalata|epascarc|cambiasoel'
    '|fansfielesncdn1|faraonrafael|observa27401323|felixhe12181981|laurabonnellyv'
    '|notidigitalrd1|nopierdo|bolivar33766257|andresvander|juvbalaguerista'
    '|alopezvalerio|leemanzanillo|eventsinfluenc1|jusanz11|el_bid|elradar_do'
    '|wendysantosb|sensacionalrd|guasabaraeditor|fuegoalalata|aquilesjimenez'
    '|fedombalrd|yocreoenfaride|carlosgabrielgc|mic_rd|lopezm00|conluisemilio'
    '|aplatanaonews|jompear|precisionportal|josebaezguerre1|jusanz11'
    '|infoturdom|arsreservas|gabsocialrd|jmarte_hijo|cristalycolores'
    '|leoneslistaprm|fansreflexiones'
)

BANK_USERS = pt.get_bank_users()

#%%
def check_username(user):
    global USERNAME_FILTER_STRING
    if user not in USERNAME_FILTER_STRING:
        USERNAME_FILTER_STRING = USERNAME_FILTER_STRING + f'|{user}'
        return USERNAME_FILTER_STRING
    else:
        print('usuario ya esta')