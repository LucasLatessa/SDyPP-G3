package com.example.demo.controller.dto;
public class ProcessRequest {

    private Integer value;

    public ProcessRequest() {
    }

    public ProcessRequest(Integer value) {
        this.value = value;
    }

    public Integer getValue() {
        return value;
    }

    public void setValue(Integer value) {
        this.value = value;
    }
}