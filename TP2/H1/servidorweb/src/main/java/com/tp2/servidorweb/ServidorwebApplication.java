package com.tp2.servidorweb;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.command.PullImageResultCallback;
import com.github.dockerjava.api.model.PortBinding;
import com.github.dockerjava.core.DockerClientBuilder;
import com.tp2.servidorweb.dto.RequestTareaRemota;
import com.tp2.servidorweb.dto.ResponseTareaRemota;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@SpringBootApplication
public class ServidorwebApplication {

    public static void main(String[] args) {
        SpringApplication.run(ServidorwebApplication.class, args);
    }    
    
    /**@GetMapping("/listadeTareas")
    public ResponseEntity<Response> listadeTareas() throws InterruptedException{
        ScriptSh ssh = new ScriptSh();
        ssh.ejecutarScript("levantar");
        
         // Espera 5 segundo para levantar contenedor y servidor flask
        Thread.sleep(5000);
        
        //Indico que recibi la peticion
        var restTemplate = new RestTemplate();
        System.out.println("Request received");
        
        //Le envio la peticion que llego al microservicio para que la resuelva
        var response = restTemplate.getForEntity("http://127.0.0.1:5000/listaTareas", ResponseTareaRemota.class);
        
        //Realizada la tarea, lo doy de baja
        ssh.ejecutarScript("detener");
        return new ResponseEntity<>(response.getBody(), response.getStatusCode());
    }

    @PostMapping("/ejecutarTareaRemota")
    public ResponseEntity<ResponseTareaRemota> ejecutarTareaRemota(@RequestBody RequestTareaRemota request) throws InterruptedException {
        //Creo la clase script y levanto el docker
        ScriptSh ssh = new ScriptSh();
        ssh.ejecutarScript("levantar");
        
         // Espera 5 segundo para levantar contenedor y servidor flask
        Thread.sleep(5000);
        
        //Indico que recibi la peticion
        var restTemplate = new RestTemplate();
        System.out.println("Request received");

        //Le envio la peticion que llego al microservicio para que la resuelva
        var response = restTemplate.postForEntity("http://127.0.0.1:5000/ejecutarTarea", request, ResponseTareaRemota.class);
        
        //Realizada la tarea, lo doy de baja
        ssh.ejecutarScript("detener");
        return new ResponseEntity<>(response.getBody(), response.getStatusCode());
    }**/
    
    @PostMapping("/ejecutarTareaRemota")
    public ResponseEntity<ResponseTareaRemota> ejecutarTareaRemota(@RequestBody RequestTareaRemota request) throws InterruptedException {
        
        //Crea el cliente docker
        DockerClient dockerClient = DockerClientBuilder.getInstance().build();
        
        //Realizo el pull
        dockerClient.pullImageCmd(request.getImagendocker()).exec(new PullImageResultCallback()).awaitCompletion();
        
        // Configura los bindings de puertos
        //Map<String, List<PortBinding>> portBindings = new HashMap<>();
        //portBindings.put("5000/tcp", Arrays.asList(PortBinding.parse("5000")));
        
        //Crea y corre el contenedor
        String contenedorId = dockerClient.createContainerCmd(request.getImagendocker())
                                          .exec()
                                          .getId();
        
        dockerClient.startContainerCmd(contenedorId).exec();
        
        //Indico que recibi la peticion
        var restTemplate = new RestTemplate();
        System.out.println("Request received");

        //Le envio la peticion que llego al microservicio para que la resuelva
        var response = restTemplate.postForEntity("http://127.0.0.1:5000/ejecutarTarea", request, ResponseTareaRemota.class);
        
        return new ResponseEntity<>(response.getBody(), response.getStatusCode());
    }
}
