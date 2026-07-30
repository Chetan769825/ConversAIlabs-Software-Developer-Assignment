const MAX_TAGS = 10;
const MAX_TAG_LENGTH = 30;
const MAX_QUERY_LENGTH = 200;
const MAX_LIMIT = 100;
const SORT_FIELDS = new Set(['createdAt', 'updatedAt', 'title']);

class InputError extends Error {}

function normalizeTags(value) {
    if (value === undefined) return undefined;
    if (!Array.isArray(value)) throw new InputError('tags must be an array of strings');
    if (value.some(tag => typeof tag !== 'string')) {
        throw new InputError('tags must contain only strings');
    }
    const tags = [...new Set(value.map(tag => tag.trim().toLowerCase()).filter(Boolean))];
    if (tags.length > MAX_TAGS) throw new InputError(`tags cannot contain more than ${MAX_TAGS} values`);
    if (tags.some(tag => tag.length > MAX_TAG_LENGTH)) {
        throw new InputError(`each tag must be at most ${MAX_TAG_LENGTH} characters`);
    }
    return tags;
}

function positiveInteger(value, name, fallback) {
    if (value === undefined) return fallback;
    if (!/^\d+$/.test(String(value)) || Number(value) < 1) {
        throw new InputError(`${name} must be a positive integer`);
    }
    return Number(value);
}

function escapeRegex(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function parseQuery(query) {
    const q = typeof query.q === 'string' ? query.q.trim() : '';
    if (q.length > MAX_QUERY_LENGTH) throw new InputError(`q must be at most ${MAX_QUERY_LENGTH} characters`);

    const rawTags = [];
    if (query.tag !== undefined) rawTags.push(query.tag);
    if (query.tags !== undefined) rawTags.push(...String(query.tags).split(','));
    const tags = normalizeTags(rawTags) || [];

    const sortBy = query.sortBy || 'updatedAt';
    const order = query.order || 'desc';
    if (!SORT_FIELDS.has(sortBy)) throw new InputError('sortBy must be createdAt, updatedAt, or title');
    if (!['asc', 'desc'].includes(order)) throw new InputError('order must be asc or desc');

    const paginated = query.page !== undefined || query.limit !== undefined;
    const page = positiveInteger(query.page, 'page', 1);
    const limit = positiveInteger(query.limit, 'limit', 20);
    if (limit > MAX_LIMIT) throw new InputError(`limit cannot exceed ${MAX_LIMIT}`);

    const filter = {};
    if (q) {
        const regex = new RegExp(escapeRegex(q), 'i');
        filter.$or = [{ title: regex }, { content: regex }];
    }
    if (tags.length) filter.tags = { $all: tags };
    return { filter, sort: { [sortBy]: order === 'asc' ? 1 : -1 }, page, limit, paginated };
}

module.exports = { InputError, normalizeTags, parseQuery };
