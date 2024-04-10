package com.tp2.servidorweb.dto;

public class ResponseTareaRemota {
    private String resultado;

    public ResponseTareaRemota() {
    }

    public ResponseTareaRemota(String resultado) {
        this.resultado = resultado;
    }

    public String getResultado() {
        return resultado;
    }

    public void setResultado(String resultado) {
        this.resultado = resultado;
    }
}
