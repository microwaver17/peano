/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Metadata } from './Metadata';
import type { SourceType } from './SourceType';

/**
 * 画像
 */
export type Image = {
    id: string;
    source_type: SourceType;
    path: string;
    belong_workspaces: Array<string>;
    metadata: Metadata;
    relative_image_ids: Array<string>;
};
