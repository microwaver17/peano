/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SourceSite } from './SourceSite';

/**
 * 取得元Webページの情報
 */
export type WebInfo = {
    source_site: SourceSite;
    id: number;
    url: string;
    url_parent: string;
};
