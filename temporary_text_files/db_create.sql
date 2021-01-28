CREATE TABLE users (
    user_id INTEGER NOT NULL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);

CREATE TABLE types (
    type_id INTEGER NOT NULL PRIMARY KEY,
    type_name TEXT NOT NULL,
    subtype TEXT NOT NULL
);

CREATE TABLE cuisines (
    cuisine_id INTEGER NOT NULL PRIMARY KEY,
    cuisine_name TEXT NOT NULL UNIQUE
);

CREATE TABLE appliances (
    appliance_id INTEGER NOT NULL PRIMARY KEY,
    appliance_name TEXT NOT NULL UNIQUE
);

CREATE TABLE recipes (
    recipe_id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    veggie BOOLEAN NOT NULL,
    vegan BOOLEAN NOT NULL,
    gluten BOOLEAN NOT NULL,
    source TEXT,
    type_id INTEGER NOT NULL REFERENCES types(type_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    cuisine_id INTEGER DEFAULT 1 REFERENCES cuisines(cuisine_id) ON UPDATE CASCADE ON DELETE SET DEFAULT,
    prep_time INTEGER,
    cook_time INTEGER,
    appliance_id INTEGER DEFAULT 1 REFERENCES appliances(appliance_id) ON UPDATE CASCADE ON DELETE SET DEFAULT,
    servings INTEGER,
    steps TEXT NOT NULL,
    notes TEXT,
    image BLOB
);

CREATE INDEX index_recipe_user ON recipes(user_id);
CREATE INDEX index_recipe_type ON recipes(type_id);
CREATE INDEX index_recipe_cuisine ON recipes(cuisine_id);
CREATE INDEX index_recipe_appliance ON recipes(appliance_id);

CREATE TABLE ingredient_units (
    unit_id INTEGER NOT NULL PRIMARY KEY,
    unit_name TEXT NOT NULL UNIQUE
);

CREATE TABLE ingredients (
    ingredient_id INTEGER NOT NULL PRIMARY KEY,
    ingredient_name TEXT NOT NULL UNIQUE,
    ingredient_type TEXT,
    ingredient_subtype TEXT
);

CREATE TABLE recipe_ingredients (
    ri_id INTEGER NOT NULL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id) ON UPDATE CASCADE ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    unit_id INTEGER NOT NULL REFERENCES ingredient_units(unit_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    size TEXT,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(ingredient_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    qualifier TEXT
);

CREATE INDEX index_ri_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX index_ri_unit ON recipe_ingredients(unit_id);
CREATE INDEX index_ri_ingredient ON recipe_ingredients(ingredient_id);

CREATE TABLE favorites (
    favorite_id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX index_favorite_user ON favorites(user_id);
CREATE INDEX index_favorite_recipe ON favorites(recipe_id);

CREATE TABLE recipe_comments (
    comment_id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE SET NULL,
    recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id) ON UPDATE CASCADE ON DELETE CASCADE,
    comment TEXT NOT NULL
);

CREATE INDEX index_rc_user ON recipe_comments(user_id);
CREATE INDEX index_rc_recipe ON recipe_comments(recipe_id);