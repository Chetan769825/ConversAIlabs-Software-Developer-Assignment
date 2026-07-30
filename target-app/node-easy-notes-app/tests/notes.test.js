const request = require('supertest');
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const { app } = require('../server');

let mongo;

beforeAll(async () => {
    mongo = await MongoMemoryServer.create();
    await mongoose.connect(mongo.getUri());
});

afterEach(async () => {
    await mongoose.connection.db.dropDatabase();
});

afterAll(async () => {
    await mongoose.disconnect();
    await mongo.stop();
});

async function create(overrides = {}) {
    return request(app).post('/notes').send({
        title: 'AI Interview',
        content: 'Prepare coding agent architecture',
        ...overrides
    });
}

test('existing CRUD behavior remains functional without tags', async () => {
    const created = await create();
    expect(created.status).toBe(201);
    expect(created.body.tags).toEqual([]);

    const list = await request(app).get('/notes');
    expect(list.status).toBe(200);
    expect(list.body).toHaveLength(1);

    const found = await request(app).get(`/notes/${created.body._id}`);
    expect(found.body.content).toBe('Prepare coding agent architecture');

    const updated = await request(app).put(`/notes/${created.body._id}`)
        .send({ title: 'Updated', content: 'New content' });
    expect(updated.status).toBe(200);
    expect(updated.body.title).toBe('Updated');

    const deleted = await request(app).delete(`/notes/${created.body._id}`);
    expect(deleted.status).toBe(200);
    expect((await request(app).get('/notes')).body).toHaveLength(0);
});

test('normalizes, trims, lowercases, removes empty and duplicate tags', async () => {
    const response = await create({ tags: [' Interview ', 'AI', 'ai', ''] });
    expect(response.status).toBe(201);
    expect(response.body.tags).toEqual(['interview', 'ai']);
});

test('legacy updates preserve existing tags', async () => {
    const note = await create({ tags: ['AI'] });
    const updated = await request(app).put(`/notes/${note.body._id}`)
        .send({ title: 'Legacy', content: 'Client omitted tags' });
    expect(updated.body.tags).toEqual(['ai']);
});

test('searches title and content case-insensitively and escapes regex', async () => {
    await create({ title: 'Roadmap', content: 'Ordinary content' });
    await create({ title: 'Other', content: 'Architecture NOTES' });
    expect((await request(app).get('/notes?q=road')).body).toHaveLength(1);
    expect((await request(app).get('/notes?q=architecture')).body).toHaveLength(1);
    expect((await request(app).get('/notes?q=.*')).body).toHaveLength(0);
});

test('filters by one or multiple tags and combines tags with search', async () => {
    await create({ title: 'Agent', tags: ['ai', 'python'] });
    await create({ title: 'Cooking', content: 'Recipe', tags: ['home'] });
    expect((await request(app).get('/notes?tag=ai')).body).toHaveLength(1);
    expect((await request(app).get('/notes?tags=ai,python')).body).toHaveLength(1);
    expect((await request(app).get('/notes?tags=ai,home')).body).toHaveLength(0);
    expect((await request(app).get('/notes?q=agent&tag=python')).body).toHaveLength(1);
});

test('sorts and paginates while preserving an array response', async () => {
    await create({ title: 'Zulu' });
    await create({ title: 'Alpha' });
    const sorted = await request(app).get('/notes?sortBy=title&order=asc');
    expect(sorted.body.map(note => note.title)).toEqual(['Alpha', 'Zulu']);
    const page = await request(app).get('/notes?page=2&limit=1&sortBy=title&order=asc');
    expect(page.body).toHaveLength(1);
    expect(page.body[0].title).toBe('Zulu');
    expect(page.headers['x-total-count']).toBe('2');
});

test.each([
    '/notes?page=0', '/notes?page=-1', '/notes?limit=0', '/notes?limit=101',
    '/notes?sortBy=content', '/notes?order=sideways'
])('rejects invalid query: %s', async path => {
    expect((await request(app).get(path)).status).toBe(400);
});

test('returns tag usage counts', async () => {
    await create({ tags: ['ai', 'python'] });
    await create({ title: 'Second', tags: ['ai'] });
    const response = await request(app).get('/notes/tags');
    expect(response.status).toBe(200);
    expect(response.body).toEqual([
        { count: 2, tag: 'ai' },
        { count: 1, tag: 'python' }
    ]);
});

test('handles malformed and missing IDs', async () => {
    expect((await request(app).get('/notes/not-an-id')).status).toBe(404);
    expect((await request(app).get(`/notes/${new mongoose.Types.ObjectId()}`)).status).toBe(404);
});

test.each([
    { tags: 'ai' },
    { tags: [42] },
    { tags: Array.from({ length: 11 }, (_, index) => `tag${index}`) },
    { tags: ['x'.repeat(31)] }
])('rejects invalid tags: %o', async body => {
    const response = await create(body);
    expect(response.status).toBe(400);
});

test('validates required content on create and update', async () => {
    expect((await request(app).post('/notes').send({ title: 'No content' })).status).toBe(400);
    const note = await create();
    expect((await request(app).put(`/notes/${note.body._id}`).send({ content: '' })).status).toBe(400);
});
