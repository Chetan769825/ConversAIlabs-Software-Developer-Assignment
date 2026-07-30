const mongoose = require('mongoose');

const NoteSchema = mongoose.Schema({
    title: String,
    content: String,
    tags: {
        type: [String],
        default: []
    }
}, {
    timestamps: true
});

NoteSchema.index({ tags: 1 });
NoteSchema.index({ updatedAt: -1 });

module.exports = mongoose.model('Note', NoteSchema);
