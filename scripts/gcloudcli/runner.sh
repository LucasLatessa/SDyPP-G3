# # EXAMPLE 1 - Basic VM + Firewall 
# # Create a static public IP address
gcloud services enable logging.googleapis.com
gcloud logging read "resource.type=gce_instance AND protoPayload.methodName=beta.compute.instances.insert"
gcloud compute ssh vm1 --zone=us-east1-b --command "cat /var/log/cloud-init-output.log"


zone=us-east1

# gcloud compute addresses create instance-public-ip --region=$zone
gcloud compute addresses create instance-public-ip --region=us-east1
# Create a firewall rule to allow traffic on port 80 / 22 
 gcloud compute firewall-rules create allow-http --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:80 --source-ranges=0.0.0.0/0
 gcloud compute firewall-rules create allow-ssh --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:22 --source-ranges=0.0.0.0/0

# Create the instance with the specified settings
gcloud compute instances create vm1      --machine-type=e2-micro      --preemptible      --image-family=ubuntu-2204-lts      --image-project=ubuntu-os-cloud      --tags=http-server      --metadata-from-file user-data=../userdata/script.sh      --zone="us-east1-b"  --address=instance-public-ip

# Delete instances
gcloud compute instances delete vm1 --zone=us-east1-b


# EXAMPLE 2 - Basic VM + SSH + Firewall + Dive into

USERNAME="lucaslatessa"; ssh-keygen -t rsa -b 4096 -C "${USERNAME}@example.com" -f ./id_rsa_example -q -N ""
# ssh-keygen -t rsa -b 4096 -C "lucaslatessa@example.com" -f ./id_rsa_example -q

# -f ./id_rsa_example: Specifies the output file name and location (./ represents the current directory).
# -q: Suppresses the key generation progress and non-error messages.
# -N "": Specifies an empty passphrase for the key pair.

gcloud compute project-info add-metadata --metadata "ssh-keys=${USERNAME}:$(cat ./id_rsa_example.pub)"
#gcloud compute project-info add-metadata --metadata "ssh-keys=lucaslatessa:$(cat ./id_rsa_example.pub)"
# STEP 3 - create the vM
 #--metadata-from-file user-data=../userdata/script.sh \
zone=us-east1-b
gcloud compute instances create vm1     --machine-type=e2-micro     --preemptible     --image-family=ubuntu-2204-lts     --image-project=ubuntu-os-cloud     --tags=http-server     --metadata="ssh-keys=$(cat ./id_rsa_example.pub)"     --metadata-from-file user-data=../userdata/script.sh     --zone="us-east1-b"     --address=instance-public-ip

# STEP 4 - Connect through GCLOÜD 
gcloud compute ssh vm1 --zone=us-east1-b --ssh-key-file=./id_rsa_example
gcloud compute ssh vm1 --zone=us-east1-b --ssh-key-file=./id_rsa_example --command "cat /var/log/cloud-init-output.log"
# EXAMPLE 1 - Basic VM + Firewall 

#gcloud compute instances get-serial-port-output vm1  --zone=us-east1-b 
gcloud compute firewall-rules create allow-ssh --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:22 --source-ranges=0.0.0.0/0
#ip="34.138.176.16"

#ssh -i  ./id_rsa_example dmpetrocelli@$ip
 ssh -i id_rsa_example dmpetrocelli@34.138.176.161



