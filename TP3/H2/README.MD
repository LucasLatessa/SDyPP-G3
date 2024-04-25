# Hit #2
Utilice #user_data para instalar paquetes (wget, htop, etc) en sus servidores Linux como defecto.
Cree reglas de seguridad para acceder a puertos necesarios en las instancias (ssh 22, http 80, https 443)
Configure SSH para poder acceder al servidor.
Conéctese por ssh y haga un wget de un archivo grande (por ejemplo ISO de ubuntu: https://releases.ubuntu.com/jammy/ubuntu-22.04.2-desktop-amd64.iso) desde su pc y uno desde la instancia virtual.  Compare y comente las velocidades de descarga. ¿A qué se debe esta diferencia?
Copie un archivo desde / hacia una Instancia (scp).
Ejemplo ejecutar:
terraform init
terraform plan
terraform apply -auto-approve
Borrar MV's:
gcloud compute ssh instancia-1 --zone=us-east1-b --ssh-key-file=./id_rsa_example
borrar instancias:
gcloud compute instances delete instancia-1 --zone=us-east1-b --quiet
gcloud compute instances delete instancia-2 --zone=us-east1-b --quiet
gcloud compute instances delete instancia-3 --zone=us-east1-b --quiet
Consectarse por SSH:
gcloud compute ssh instancia-1 --zone=us-east1-b 
gcloud compute ssh instancia-2 --zone=us-east1-b 
gcloud compute ssh instancia-3 --zone=us-east1-b 
Wget de un archivo grande (ISO de ubuntu):
gcloud compute ssh instancia-1 --command="wget https://releases.ubuntu.com/jammy/ubuntu-22.04.2-desktop-amd64.iso"
gcloud compute ssh instancia-1 --command="wget -P /tmp https://releases.ubuntu.com/22.04.4/ubuntu-22.04.4-desktop-amd64.iso?_gl=1*x2gb7b*_gcl_au*MTU0MjgwMTg3OC4xNzEzODk2Njk2&_ga=2.3701936.1611293198.1713896696-400394319.1713896696"

# Copia de Maquina virtual a maquina local
gcloud compute scp --recurse instancia-1:/home/Leone/prueba.txt .

# Copia de Maquina local a maquina virtual
gcloud compute scp ./prueba.txt instancia-1:/home/Leone