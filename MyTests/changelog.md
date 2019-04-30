

**Obsinfo ==> SISMOBinfo**

  

 ## Les modifications apportées aux inputs files

  

_**Général**_

  

- Format de date : exemple 2012-01-02T02:02:03 (date_time_Z)

- Comment: objet Obspy ( BeginEffectiveTime,End,,,values, authors,,)

_**Network**_

- General_informations: ajout des auteurs des commentaires: objet Obspy

  

**Satation**

- Start_time et end_time

- Additional properties ( ou ajouté: 'restrictedStatus')

  

**Channel**

- start_date et end_time dans channels : pour sismob
- localisation_method, clock_corrections : pas pour sismob

  

**instrument :**

- Preamplifier non obligatoire,

- location_code => station_code, On prefere l’avoir dans la station parce que nous pouvons avoir +ieurs instruments.

**Filter et response**:

- gain : {value : 0.225, frequency: 0} => sensitivity ?

- input_units , output_units : Premiére lettre en majuscule.

- ajout d'autres proprités dans les pz,

- dipType and aumuth type : une valeur

- on a des stages sans filtre.

  

## PZ 

  

- decimation_factor => nous c’est Decimation_factor (majuscule:) )

- ['input_sr'] vous le calculrer nous c’est : stage['**Input_sampling_interval**']

- type de filtre[filter][type] => nous c’est stage[**Transfer_function_type**]

- delay: donner par le constructeur (souvent 0) => vous float(decim['offset'])/float(decim['input_sr']))

- ["FIR","FIR_SYM_1","FIR_SYM_2"] type filter

- Le mot clé symmetry on l’a pas dans non PZ,

- __get_units_sensitivity : modifié selon notre structure .
- get_gain : gain ==sensitivity

- azimuth : valeur, on ne la calcule pas ( dans station)
