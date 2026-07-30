const mongoose = require('mongoose');
const Note = require('../models/note.model.js');
const { InputError, normalizeTags, parseQuery } = require('../utils/note.validation.js');

function badRequest(res, error) {
    return res.status(400).send({ message: error.message });
}

function notFound(res, id) {
    return res.status(404).send({ message: `Note not found with id ${id}` });
}

function validId(id) {
    return mongoose.isValidObjectId(id);
}

exports.create = async (req, res) => {
    if (!req.body.content) return badRequest(res, new InputError('Note content can not be empty'));
    try {
        const note = await Note.create({
            title: req.body.title || 'Untitled Note',
            content: req.body.content,
            tags: normalizeTags(req.body.tags) || []
        });
        return res.status(201).send(note);
    } catch (error) {
        if (error instanceof InputError) return badRequest(res, error);
        return res.status(500).send({ message: 'Some error occurred while creating the Note.' });
    }
};

exports.findAll = async (req, res) => {
    try {
        const options = parseQuery(req.query);
        let query = Note.find(options.filter).sort(options.sort);
        if (options.paginated) query = query.skip((options.page - 1) * options.limit).limit(options.limit);
        const notes = await query;
        if (options.paginated) {
            const total = await Note.countDocuments(options.filter);
            res.set({
                'X-Total-Count': String(total),
                'X-Page': String(options.page),
                'X-Limit': String(options.limit)
            });
        }
        return res.send(notes);
    } catch (error) {
        if (error instanceof InputError) return badRequest(res, error);
        return res.status(500).send({ message: 'Some error occurred while retrieving notes.' });
    }
};

exports.findTags = async (_req, res) => {
    try {
        const tags = await Note.aggregate([
            { $unwind: '$tags' },
            { $group: { _id: '$tags', count: { $sum: 1 } } },
            { $sort: { count: -1, _id: 1 } },
            { $project: { _id: 0, tag: '$_id', count: 1 } }
        ]);
        return res.send(tags);
    } catch (_error) {
        return res.status(500).send({ message: 'Some error occurred while retrieving tags.' });
    }
};

exports.findOne = async (req, res) => {
    if (!validId(req.params.noteId)) return notFound(res, req.params.noteId);
    try {
        const note = await Note.findById(req.params.noteId);
        return note ? res.send(note) : notFound(res, req.params.noteId);
    } catch (_error) {
        return res.status(500).send({ message: `Error retrieving note with id ${req.params.noteId}` });
    }
};

exports.update = async (req, res) => {
    if (!req.body.content) return badRequest(res, new InputError('Note content can not be empty'));
    if (!validId(req.params.noteId)) return notFound(res, req.params.noteId);
    try {
        const update = { title: req.body.title || 'Untitled Note', content: req.body.content };
        const tags = normalizeTags(req.body.tags);
        if (tags !== undefined) update.tags = tags;
        const note = await Note.findByIdAndUpdate(req.params.noteId, update, {
            new: true, runValidators: true
        });
        return note ? res.send(note) : notFound(res, req.params.noteId);
    } catch (error) {
        if (error instanceof InputError) return badRequest(res, error);
        return res.status(500).send({ message: `Error updating note with id ${req.params.noteId}` });
    }
};

exports.delete = async (req, res) => {
    if (!validId(req.params.noteId)) return notFound(res, req.params.noteId);
    try {
        const note = await Note.findByIdAndDelete(req.params.noteId);
        return note ? res.send({ message: 'Note deleted successfully!' }) : notFound(res, req.params.noteId);
    } catch (_error) {
        return res.status(500).send({ message: `Could not delete note with id ${req.params.noteId}` });
    }
};
