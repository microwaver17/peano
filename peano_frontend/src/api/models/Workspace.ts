/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { RemoteSource } from './RemoteSource';

/**
 * ワークスペース
 */
export type Workspace = {
    name: string;
    scan_directories: Array<string>;
    scan_remotes: Record<string, RemoteSource>;
    ignore_patterns: Array<string>;
    mean: Array<number>;
};
