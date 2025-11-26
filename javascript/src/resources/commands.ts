/**
 * Commands resource - Shell command execution
 */

import { HTTPClient } from '../client.js';
import type { CommandResponse, CommandOptions } from '../types/index.js';

export class Commands {
  constructor(private client: HTTPClient) {}

  /**
   * Run shell command
   *
   * ALL commands (sync and background) are automatically wrapped in `bash -c` for
   * proper shell feature support (pipes, redirects, variables, etc.)
   *
   * Python reference: _base_commands.py - both sync and background use bash wrapper
   */
  async run(command: string, options?: CommandOptions): Promise<CommandResponse> {
    // ✅ CRITICAL: Wrap ALL commands (sync + background) in bash for shell features
    // This matches Python SDK behavior exactly
    // Default timeouts: sync 30s, background 120s
    const apiTimeout = options?.timeout || (options?.background ? 120 : 30);
    // HTTP timeout: background returns immediately (30s), sync needs buffer (API + 30s)
    const httpTimeout = options?.background ? 30000 : (apiTimeout + 30) * 1000;

    const payload: any = {
      command: 'bash',
      args: ['-c', command],
      timeout: apiTimeout,
      workdir: options?.workingDir || '/workspace',
    };

    if (options?.env) {
      payload.env = options.env;
    }

    const response = await this.client.post<CommandResponse>(
      options?.background ? '/commands/background' : '/commands/run',
      payload,
      { timeout: httpTimeout }
    );
    return response;
  }

  /**
   * Run command in background
   *
   * Commands are automatically wrapped in `bash -c` for proper shell feature support
   * (pipes, redirects, variables, etc.)
   */
  async runBackground(command: string, options?: Omit<CommandOptions, 'background'>): Promise<{ process_id: string }> {
    // ✅ CRITICAL: Wrap command in bash for shell features
    // Default timeout: 120s (suitable for package installs and builds)
    const apiTimeout = options?.timeout || 120;
    // Background operations return immediately - 30s HTTP timeout is sufficient
    const httpTimeout = 30000;

    const payload: any = {
      command: 'bash',
      args: ['-c', command],
      timeout: apiTimeout,
      workdir: options?.workingDir || '/workspace',
    };

    if (options?.env) {
      payload.env = options.env;
    }

    const response = await this.client.post<{ process_id: string }>(
      '/commands/background',
      payload,
      { timeout: httpTimeout }
    );
    return response;
  }
}

