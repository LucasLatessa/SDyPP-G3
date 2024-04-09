package com.tp2.servidorweb;

import com.tp2.servidorweb.dto.ScriptSh;
import com.tp2.servidorweb.dto.ProcessResponse;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@SpringBootApplication
public class ServidorwebApplication {

    public static void main(String[] args) {
        SpringApplication.run(ServidorwebApplication.class, args);
    }

    @GetMapping("/process")
    public ResponseEntity<ProcessResponse> process() throws InterruptedException {
        //Creo la clase script y levanto el docker
        ScriptSh ssh = new ScriptSh();
        ssh.ejecutarScript("levantar");
        
         // Espera 5 segundo para levantar contenedor y servidor flask
        Thread.sleep(5000);
        
        //Indico que recibi la peticion
        var restTemplate = new RestTemplate();
        System.out.println("Request received");

        //Le envio la peticion que llego al microservicio para que la resuelva
        var response = restTemplate.getForEntity("http://127.0.0.1:5000/process", ProcessResponse.class);
        
        //Realizada la tarea, lo doy de baja
        ssh.ejecutarScript("detener");
        return new ResponseEntity<>(response.getBody(), response.getStatusCode());
    }

}
