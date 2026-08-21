#!/usr/bin/env node

const args = process.argv.slice(2);

function help(): void {
    console.log(`
iDeez CLI

Usage:
  npx ideez <command>

Commands:
  health              Check iDeez API status
  version             Show CLI version
  help                Show this help

Environment:
  IDEEZ_API_KEY       API key
  IDEEZ_API_URL       API base URL
`);
}

async function health(): Promise<void> {
    const baseUrl =
        process.env.IDEEZ_API_URL ??
        "https://api.ideez.dev";

    const response = await fetch(
        `${baseUrl.replace(/\/+$/, "")}/health`,
    );

    const data = await response.json();

    console.log(JSON.stringify(data, null, 2));

    if (!response.ok) {
        process.exitCode = 1;
    }
}

async function main(): Promise<void> {
    const command = args[0] ?? "help";

    switch (command) {
        case "health":
            await health();
            break;

        case "version":
            console.log("iDeez CLI 1.0.0");
            break;

        case "help":
        case "--help":
        case "-h":
            help();
            break;

        default:
            console.error(`Unknown command: ${command}`);
            help();
            process.exitCode = 1;
    }
}

main().catch((error) => {
    console.error(
        error instanceof Error
            ? error.message
            : String(error),
    );
    process.exitCode = 1;
});