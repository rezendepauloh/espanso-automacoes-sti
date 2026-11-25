use std::process::ExitCode;
use sti_forms::{CliOptions, run_cli};

fn print_help() {
    eprintln!(
        "Uso: sti-forms (--form <nome> | --form-config <caminho.yml>) [--json] [--dump-resolved]"
    );
}

fn parse_args() -> Result<Option<CliOptions>, String> {
    let mut args = std::env::args().skip(1);
    let mut form_name = None;
    let mut form_config = None;
    let mut json_output = false;
    let mut dump_resolved = false;

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "-h" | "--help" => {
                print_help();
                return Ok(None);
            }
            "--form" => {
                form_name = Some(
                    args.next()
                        .ok_or_else(|| "Faltou o nome após --form.".to_string())?,
                );
            }
            "--form-config" => {
                form_config = Some(
                    args.next()
                        .ok_or_else(|| "Faltou o caminho após --form-config.".to_string())?,
                );
            }
            "--json" => json_output = true,
            "--dump-resolved" => dump_resolved = true,
            other => {
                return Err(format!("Argumento desconhecido: {other}"));
            }
        }
    }

    if form_name.is_none() && form_config.is_none() {
        return Err("Informe --form <nome> ou --form-config <caminho.yml>.".to_string());
    }

    Ok(Some(CliOptions {
        form_name,
        form_config,
        json_output,
        dump_resolved,
    }))
}

fn main() -> ExitCode {
    let opts = match parse_args() {
        Ok(Some(o)) => o,
        Ok(None) => return ExitCode::SUCCESS,
        Err(msg) => {
            eprintln!("Erro: {msg}");
            print_help();
            return ExitCode::from(2);
        }
    };

    match run_cli(opts) {
        Ok(Some(output)) => {
            print!("{output}");
            ExitCode::SUCCESS
        }
        Ok(None) => ExitCode::from(1),
        Err(err) => {
            eprintln!("{err}");
            ExitCode::from(1)
        }
    }
}
