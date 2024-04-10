package com.tp2.servidorweb.dto;


public class RequestTareaRemota {
    private String imagen;
    private String operador;
    private int n1;
    private int n2;
    
    public RequestTareaRemota() {
    }

    public RequestTareaRemota(String imagen, String operador, int n1, int n2) {
        this.imagen = imagen;
        this.operador = operador;
        this.n1 = n1;
        this.n2 = n2;
    }

    public String getImagen() {
        return imagen;
    }

    public void setImagen(String imagen) {
        this.imagen = imagen;
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

