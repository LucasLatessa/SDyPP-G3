package com.tp2.servidorweb.dto;

import java.io.File;
import java.io.FileWriter;
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

    public void crearBat(String script, String imagen) {
        String extension;

        try {

            boolean isWindows = System.getProperty("os.name").toLowerCase().startsWith("windows");

            //Si es windows o otro sistema, la extension cambia
            if (isWindows) {
                extension = ".bat";
            } else {
                extension = ".sh";
            }

            File batFile = new File(script + extension); //Poner nombre del string
            FileWriter writer = new FileWriter(batFile);

            if (script == "levantar") {
                writer.write("docker pull " + imagen + "\n");
                writer.write("docker run --rm --name tarea -p 5000:5000 " + imagen);
            } else if (script == "detener") {
                writer.write("docker stop tarea");
            }

            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
