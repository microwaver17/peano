/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { MLTag } from './MLTag';

/**
 * 機械学習(danbooru-pretrained)で得られた情報
 */
export type MLDanbooru = {
    tags: Array<MLTag>;
    feature: Array<number>;
};
