/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { FileInfo } from './FileInfo';
import type { MLDanbooru } from './MLDanbooru';
import type { WebInfo } from './WebInfo';

/**
 * 画像のメタデータ
 */
export type Metadata = {
    title: string;
    author: string;
    tags: Array<string>;
    description: string;
    misc_info: string;
    image_size: Array<number>;
    last_updated: string;
    file_info: FileInfo;
    web_info?: WebInfo;
    ml?: MLDanbooru;
};
