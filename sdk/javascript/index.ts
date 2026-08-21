export interface IDeezClientOptions {
    apiKey: string;
    baseUrl?: string;
    timeout?: number;
}

export class IDeezError extends Error {
    readonly status: number;
    constructor(message: string, status: number) {
        super(message);
        this.name = "IDeezError";
        this.status = status;
    }
}

export class IDeezClient {
    private readonly apiKey: string;
    private readonly baseUrl: string;
    private readonly timeout: number;

    constructor(options: IDeezClientOptions) {
        if (!options.apiKey) {throw new Error("apiKey is required");}

        this.apiKey = options.apiKey;
        this.baseUrl = (options.baseUrl ?? "https://api.ideez.dev").replace(/\/+$/, "");
        this.timeout = options.timeout ?? 15000;
    }

    async health(): Promise<Record<string, unknown>> {
        return this.request("/health", {
            method: "GET",
        });
    }

    async createSession(userId: string, data: Record<string, unknown> = {}): Promise<Record<string, unknown>> {
        return this.request("/api/v1/sessions", {
            method: "POST",
            body: JSON.stringify({
                user_id: userId,
                ...data,
            }),
        });
    }

    async verifyPin(pin: string): Promise<Record<string, unknown>> {
        return this.request("/api/v1/pin/verify", {
            method: "POST",
            body: JSON.stringify({ pin }),
        });
    }

    async revokeSession(sessionId: string): Promise<Record<string, unknown>> {
        return this.request(
            `/api/v1/sessions/${sessionId}/revoke`,
            { method: "POST" },
        );
    }

    private async request(path: string, init: RequestInit): Promise<Record<string, unknown>> {
        const controller = new AbortController();
        const timeout = setTimeout(
            () => controller.abort(),
            this.timeout,
        );

        try {
            const response = await fetch(
                `${this.baseUrl}${path}`,
                {
                    ...init,
                    signal: controller.signal,
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${this.apiKey}`,
                        ...(init.headers ?? {}),
                    },
                },
            );

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new IDeezError(
                    `iDeez API error: ${response.status}`,
                    response.status,
                );
            }

            return data;
        } finally {
            clearTimeout(timeout);
        }
    }
}

export default IDeezClient;