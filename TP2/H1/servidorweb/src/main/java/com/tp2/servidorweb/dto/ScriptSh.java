package com.tp2.servidorweb.dto;

import java.io.IOException;

//Script que ejecuta .sh o .bat, segun el sistema operativo
public class ScriptSh {

    public void ejecutarScript(String script) {
        try {
            //Determino si es windows o no
            boolean isWindows = System.getProperty("os.name").toLowerCase().startsWith("windows");

            //Clase para crear procesos del SO
            ProcessBuilder pb = new ProcessBuilder();

            //Si es windows o otro sistema, el path cambia
            if (isWindows) {
                pb.command(System.getProperty("user.dir") + "\\" + script + ".bat");
            } else {
                pb.command("sh", "-c", System.getProperty("user.dir") + "/" + script + ".sh");
            }

            //Ejecuto el proceso
            Process process = pb.start();
            
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
}   
