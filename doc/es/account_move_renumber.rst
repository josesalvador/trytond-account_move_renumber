#:after:account/account:section:cierre#

======================
Renumerar los asientos
======================

**Tryton** nos ofrece un asistente con el cuál podemos reneumerar los asientos, 
una función que nos será muy útil en el cierre, y sobre todo, reapertura del 
año ya que será cuando lo usaremos. 

.. view:: move_renumber_start_view_form

Al abrirse el asistente situado en el menu |menu_move_renumber| veremos dos 
campos a rellenar, dónde introducir información. En el primero deberemos 
seleccionar el *Ejercicio fiscal* el cuál queremos renumerar los asientos y en 
el segundo, *Primer número*, el número con el que queremos que la renumeración 
de comienzo. Por defecto, el sistema nos ofrecerá el número 1, esto se podrá 
modificar a números posteriores si tenemos algún asiento al inicio o de apertura 
que nos falta introducir. 

.. |menu_move_renumber| tryref:: account_move_renumber.menu_move_renumber/complete_name
