package com.tp2.servidorweb.dto;


public class RequestTareaRemota {
    private String imagendocker;
    private String operador;
    private int n1;
    private int n2;
    
    public RequestTareaRemota() {
    }

    public RequestTareaRemota(String imagendocker, String operador, int n1, int n2) {
        this.imagendocker = imagendocker;
        this.operador = operador;
        this.n1 = n1;
        this.n2 = n2;
    }

    public String getImagendocker() {
        return imagendocker;
    }

    public void setImagendocker(String imagendocker) {
        this.imagendocker = imagendocker;
    }

    public String getOperador() {
        return operador;
    }

    public void setOperador(String operador) {
        this.operador = operador;
    }

    public int getN1() {
        return n1;
    }

    public void setN1(int n1) {
        this.n1 = n1;
    }

    public int getN2() {
        return n2;
    }

    public void setN2(int n2) {
        this.n2 = n2;
    }
    
    
    
}

