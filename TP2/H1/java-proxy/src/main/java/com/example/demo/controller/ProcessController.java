package com.example.demo.controller;

import com.example.demo.controller.dto.ProcessResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
//proxy
@RestController
public class ProcessController {

    @GetMapping("/process")
    public ResponseEntity<ProcessResponse> process() {
        var restTemplate = new RestTemplate();
        System.out.println("Request received");

        var response = restTemplate.getForEntity("http://127.0.0.1:5000/process", ProcessResponse.class);
        return new ResponseEntity<>(response.getBody(), response.getStatusCode());
    }

}
/* //sync calls 
@RestController
public class ProcessController {

    @GetMapping("/process")
    public ResponseEntity<ProcessResponse> process() {
        var restTemplate = new RestTemplate();
        System.out.println("Request received");
        var request = new ProcessRequest(43);
        var response = restTemplate.postForEntity("http://127.0.0.1:6000/process", request, ProcessResponse.class);

        ProcessRequest request2 = new ProcessRequest(42);
        var response2 = restTemplate.postForEntity("http://127.0.0.1:6001/process", request2, ProcessResponse.class);

        var finalResponse = new ProcessResponse(response.getBody().getData() + response2.getBody().getData());
        return new ResponseEntity<>(finalResponse, HttpStatus.OK);
    }

} */

/* //async calls
@RestController
public class ProcessController {

    private WebClient webClient(String url) {
        return WebClient.builder().baseUrl(url).build();
    }

    @GetMapping("/process")
    public ResponseEntity<ProcessResponse> process() {

        System.out.println("Request received");

        Mono<ProcessResponse> responseMono1 = webClient("http://127.0.0.1:6000")
                .post()
                .uri("/process")
                .body(BodyInserters.fromValue(new ProcessRequest(42)))
                .retrieve()
                .bodyToMono(ProcessResponse.class);

        Mono<ProcessResponse> responseMono2 = webClient("http://127.0.0.1:6001")
                .post()
                .uri("/process")
                .body(BodyInserters.fromValue(new ProcessRequest(41)))
                .retrieve()
                .bodyToMono(ProcessResponse.class);

        Mono<Integer> resultMono = Mono.zip(responseMono1, responseMono2)
                .map(tuple -> tuple.getT1().getData() + tuple.getT2().getData());

        return resultMono
                .map(sum -> new ResponseEntity<>(new ProcessResponse(sum), HttpStatus.OK))
                .block();

    }

} */