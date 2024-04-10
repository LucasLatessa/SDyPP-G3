package com.tp2.servidorweb;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.command.PullImageResultCallback;
import com.github.dockerjava.core.DockerClientBuilder;
import com.tp2.servidorweb.dto.RequestTareaRemota;
import com.tp2.servidorweb.dto.ResponseTareaRemota;
import com.tp2.servidorweb.dto.ScriptSh;
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

    @PostMapping("/ejecutarTareaRemota")
    public ResponseEntity<ResponseTareaRemota> ejecutarTareaRemota(@RequestBody RequestTareaRemota request) throws InterruptedException {
        //Creo la clase script y levanto el docker
        ScriptSh ssh = new ScriptSh();
        
        ssh.crearBat("levantar", request.getImagen());
        ssh.ejecutarScript("levantar");
        
         // Espera 5 segundo para levantar contenedor y servidor flask
        Thread.sleep(5000);
        
        //Indico que recibi la peticion
        var restTemplate = new RestTemplate();
        System.out.println("Request received");

        //Le envio la peticion que llego al microservicio para que la resuelva
        var response = restTemplate.postForEntity("http://127.0.0.1:5000/ejecutarTarea", request, ResponseTareaRemota.class);
        
        //Realizada la tarea, lo doy de baja
        ssh.crearBat("detener", null);
        ssh.ejecutarScript("detener");
        return new ResponseEntity<>(response.getBody(), response.getStatusCode());
    }
}
