/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SourceSite } from './SourceSite';

/**
 * 新しい画像をWebページから取得する方法
 */
export type RemoteSource = {
    name: string;
    site: SourceSite;
    query: string;
};
