package mytest1;

import io.micronaut.configuration.picocli.PicocliRunner;
import io.micronaut.context.ApplicationContext;

import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;

@Command(name = "mytest1", description = "...",
        mixinStandardHelpOptions = true)
public class Mytest1Command implements Runnable {

    @Option(names = {"-v", "--verbose"}, description = "...")
    boolean verbose;

    public static void main(String[] args) throws Exception {
        PicocliRunner.run(Mytest1Command.class, args);
    }

    public void run() {
        // business logic here
        //if (verbose) {
            System.out.println("Github hi from mytest1!");
        //}
    }
}
