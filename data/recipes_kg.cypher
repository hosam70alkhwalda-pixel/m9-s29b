// Module 9 Week B — Stretch Thu (GraphRAG) — fixture subgraph
// ~80-node subset of the Lab W9B recipe knowledge graph.
//
// Schema (subset of the canonical W9B recipe schema):
//   Labels: Recipe, Cuisine, Ingredient, Author, Technique — every node also :Entity
//   Relationships:
//     (:Recipe)-[:USES_INGREDIENT]->(:Ingredient)
//     (:Recipe)-[:OF_CUISINE]->(:Cuisine)
//     (:Recipe)-[:BY_AUTHOR]->(:Author)
//     (:Recipe)-[:REQUIRES_TECHNIQUE]->(:Technique)
//     (:Cuisine)-[:SUBCLASS_OF]->(:Cuisine)
//
// Counts (asserted by load_fixture.py):
//   :Recipe = 50, :Cuisine = 8, :Ingredient = 15, :Author = 5, :Technique = 5
//   Total nodes = 83
//
// Recipe descriptions are short, distinctive natural-language sentences
// designed for embedding-based retrieval.
//
// Structural-context design.
//   40 of the 50 recipes have full structural context (cuisine + author +
//   ingredients), so fuse() awards them the full +0.3 boost.
//   10 recipes ship deliberately context-bare — they are vector-indexed
//   (description + embedding) but carry no :OF_CUISINE, :BY_AUTHOR, or
//   :USES_INGREDIENT edges. fuse() therefore awards them 0 boost, and a
//   correct fusion implementation demotes them below context-rich gold
//   recipes whose vector scores are close. The bare recipes are 008, 010,
//   014, 017, 018, 019, 024, 030, 034, 039 — search for "bare-context"
//   in this file to see the commented-out relationship statements. This
//   is what makes test_fusion_changes_ranking_from_vector_alone a real
//   gate (a learner who bypasses the structural boost would produce a
//   fused ranking identical to the vector ranking on every query).

// ---- Identity Discipline constraint ---------------------------------------
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
  FOR (n:Entity) REQUIRE n.id IS UNIQUE;

// ---- Cuisines (8, with 3-level hierarchy) ---------------------------------
MERGE (:Cuisine:Entity {id: 'cuisine:world',    name: 'World'});
MERGE (:Cuisine:Entity {id: 'cuisine:asian',    name: 'Asian'});
MERGE (:Cuisine:Entity {id: 'cuisine:european', name: 'European'});
MERGE (:Cuisine:Entity {id: 'cuisine:chinese',  name: 'Chinese'});
MERGE (:Cuisine:Entity {id: 'cuisine:sichuan',  name: 'Sichuan'});
MERGE (:Cuisine:Entity {id: 'cuisine:italian',  name: 'Italian'});
MERGE (:Cuisine:Entity {id: 'cuisine:japanese', name: 'Japanese'});
MERGE (:Cuisine:Entity {id: 'cuisine:mexican',  name: 'Mexican'});

MATCH (a:Cuisine {id: 'cuisine:asian'}),    (w:Cuisine {id: 'cuisine:world'})    MERGE (a)-[:SUBCLASS_OF]->(w);
MATCH (e:Cuisine {id: 'cuisine:european'}), (w:Cuisine {id: 'cuisine:world'})    MERGE (e)-[:SUBCLASS_OF]->(w);
MATCH (m:Cuisine {id: 'cuisine:mexican'}),  (w:Cuisine {id: 'cuisine:world'})    MERGE (m)-[:SUBCLASS_OF]->(w);
MATCH (c:Cuisine {id: 'cuisine:chinese'}),  (a:Cuisine {id: 'cuisine:asian'})    MERGE (c)-[:SUBCLASS_OF]->(a);
MATCH (j:Cuisine {id: 'cuisine:japanese'}), (a:Cuisine {id: 'cuisine:asian'})    MERGE (j)-[:SUBCLASS_OF]->(a);
MATCH (s:Cuisine {id: 'cuisine:sichuan'}),  (c:Cuisine {id: 'cuisine:chinese'})  MERGE (s)-[:SUBCLASS_OF]->(c);
MATCH (i:Cuisine {id: 'cuisine:italian'}),  (e:Cuisine {id: 'cuisine:european'}) MERGE (i)-[:SUBCLASS_OF]->(e);

// ---- Ingredients (15) -----------------------------------------------------
MERGE (:Ingredient:Entity {id: 'ingredient:ginger',           name: 'ginger',           category: 'spice'});
MERGE (:Ingredient:Entity {id: 'ingredient:garlic',           name: 'garlic',           category: 'aromatic'});
MERGE (:Ingredient:Entity {id: 'ingredient:soy-sauce',        name: 'soy sauce',        category: 'condiment'});
MERGE (:Ingredient:Entity {id: 'ingredient:szechuan-pepper',  name: 'szechuan peppercorn', category: 'spice'});
MERGE (:Ingredient:Entity {id: 'ingredient:chili',            name: 'chili',            category: 'spice'});
MERGE (:Ingredient:Entity {id: 'ingredient:chicken',          name: 'chicken',          category: 'meat'});
MERGE (:Ingredient:Entity {id: 'ingredient:tofu',             name: 'tofu',             category: 'protein'});
MERGE (:Ingredient:Entity {id: 'ingredient:basil',            name: 'basil',            category: 'herb'});
MERGE (:Ingredient:Entity {id: 'ingredient:tomato',           name: 'tomato',           category: 'vegetable'});
MERGE (:Ingredient:Entity {id: 'ingredient:mozzarella',       name: 'mozzarella',       category: 'dairy'});
MERGE (:Ingredient:Entity {id: 'ingredient:olive-oil',        name: 'olive oil',        category: 'oil'});
MERGE (:Ingredient:Entity {id: 'ingredient:nori',             name: 'nori',             category: 'seaweed'});
MERGE (:Ingredient:Entity {id: 'ingredient:rice',             name: 'rice',             category: 'grain'});
MERGE (:Ingredient:Entity {id: 'ingredient:lime',             name: 'lime',             category: 'fruit'});
MERGE (:Ingredient:Entity {id: 'ingredient:cilantro',         name: 'cilantro',         category: 'herb'});

// ---- Authors (5) ----------------------------------------------------------
MERGE (:Author:Entity {id: 'author:rossi',  name: 'Maria Rossi',  country: 'Italy'});
MERGE (:Author:Entity {id: 'author:tanaka', name: 'Hiro Tanaka',  country: 'Japan'});
MERGE (:Author:Entity {id: 'author:chen',   name: 'Wei Chen',     country: 'China'});
MERGE (:Author:Entity {id: 'author:reyes',  name: 'Sofia Reyes',  country: 'Mexico'});
MERGE (:Author:Entity {id: 'author:smith',  name: 'Alex Smith',   country: 'United States'});

// ---- Techniques (5) -------------------------------------------------------
MERGE (:Technique:Entity {id: 'technique:stir-fry', name: 'stir-fry'});
MERGE (:Technique:Entity {id: 'technique:bake',     name: 'bake'});
MERGE (:Technique:Entity {id: 'technique:grill',    name: 'grill'});
MERGE (:Technique:Entity {id: 'technique:simmer',   name: 'simmer'});
MERGE (:Technique:Entity {id: 'technique:roll',     name: 'roll'});

// ---- Recipes (50) — distinct, embedding-friendly descriptions -------------

MERGE (r:Recipe:Entity {id: 'recipe:001'}) SET r.name = 'Mapo Tofu', r.description = 'Silky tofu braised in a fiery sichuan sauce with peppercorn heat and fermented bean paste.', r.popularityScore = 92, r.prepMinutes = 35;
MERGE (r:Recipe:Entity {id: 'recipe:002'}) SET r.name = 'Kung Pao Chicken', r.description = 'Stir-fried spicy chicken with peanuts, dried chilies, and tingling szechuan peppercorn.', r.popularityScore = 95, r.prepMinutes = 25;
MERGE (r:Recipe:Entity {id: 'recipe:003'}) SET r.name = 'Dan Dan Noodles', r.description = 'Hand-pulled noodles in a chili oil broth with minced pork and crunchy preserved vegetables.', r.popularityScore = 88, r.prepMinutes = 40;
MERGE (r:Recipe:Entity {id: 'recipe:004'}) SET r.name = 'Twice-Cooked Pork', r.description = 'Pork belly first simmered then stir-fried with leeks and chili bean paste.', r.popularityScore = 80, r.prepMinutes = 50;
MERGE (r:Recipe:Entity {id: 'recipe:005'}) SET r.name = 'Sichuan Boiled Beef', r.description = 'Tender beef slices poached in a numbing broth of sichuan peppercorn and dried chilies.', r.popularityScore = 86, r.prepMinutes = 45;

MERGE (r:Recipe:Entity {id: 'recipe:006'}) SET r.name = 'Cantonese Ginger Chicken', r.description = 'Whole chicken steamed gently with fresh ginger, scallions, and sesame oil.', r.popularityScore = 78, r.prepMinutes = 60;
MERGE (r:Recipe:Entity {id: 'recipe:007'}) SET r.name = 'Garlic Soy Stir-fried Greens', r.description = 'Leafy greens flash-fried with garlic and a splash of soy sauce.', r.popularityScore = 70, r.prepMinutes = 10;
MERGE (r:Recipe:Entity {id: 'recipe:008'}) SET r.name = 'Sweet and Sour Chicken', r.description = 'Crisp battered chicken tossed in a glossy sweet vinegar sauce with pineapple.', r.popularityScore = 82, r.prepMinutes = 35;
MERGE (r:Recipe:Entity {id: 'recipe:009'}) SET r.name = 'Steamed Pork Buns', r.description = 'Fluffy white buns filled with sweet barbecued pork.', r.popularityScore = 84, r.prepMinutes = 90;
MERGE (r:Recipe:Entity {id: 'recipe:010'}) SET r.name = 'Egg Fried Rice', r.description = 'Day-old rice tossed quickly in a hot wok with scrambled egg and scallion.', r.popularityScore = 76, r.prepMinutes = 15;

MERGE (r:Recipe:Entity {id: 'recipe:011'}) SET r.name = 'Margherita Pizza', r.description = 'Charred neapolitan pizza topped with tomato, fresh mozzarella, and basil leaves.', r.popularityScore = 96, r.prepMinutes = 30;
MERGE (r:Recipe:Entity {id: 'recipe:012'}) SET r.name = 'Spaghetti al Pomodoro', r.description = 'Simple spaghetti tossed in a slow-simmered tomato and basil sauce.', r.popularityScore = 90, r.prepMinutes = 25;
MERGE (r:Recipe:Entity {id: 'recipe:013'}) SET r.name = 'Caprese Salad', r.description = 'Sliced tomato and mozzarella layered with basil and drizzled with olive oil.', r.popularityScore = 85, r.prepMinutes = 8;
MERGE (r:Recipe:Entity {id: 'recipe:014'}) SET r.name = 'Pesto Genovese Pasta', r.description = 'Trofie pasta coated in a bright basil pesto with pine nuts and parmesan.', r.popularityScore = 87, r.prepMinutes = 20;
MERGE (r:Recipe:Entity {id: 'recipe:015'}) SET r.name = 'Lasagna Bolognese', r.description = 'Layered pasta with slow-cooked meat ragu, bechamel, and parmesan, baked until golden.', r.popularityScore = 91, r.prepMinutes = 120;
MERGE (r:Recipe:Entity {id: 'recipe:016'}) SET r.name = 'Risotto alla Milanese', r.description = 'Creamy saffron risotto finished with butter and parmesan.', r.popularityScore = 83, r.prepMinutes = 35;
MERGE (r:Recipe:Entity {id: 'recipe:017'}) SET r.name = 'Tiramisu', r.description = 'Espresso-soaked ladyfingers layered with mascarpone cream and dusted cocoa.', r.popularityScore = 89, r.prepMinutes = 30;
MERGE (r:Recipe:Entity {id: 'recipe:018'}) SET r.name = 'Focaccia with Rosemary', r.description = 'Olive oil bread dimpled and baked with rosemary and flaky sea salt.', r.popularityScore = 79, r.prepMinutes = 180;
MERGE (r:Recipe:Entity {id: 'recipe:019'}) SET r.name = 'Cacio e Pepe', r.description = 'Pasta tossed with pecorino cheese and freshly cracked black pepper.', r.popularityScore = 88, r.prepMinutes = 15;
MERGE (r:Recipe:Entity {id: 'recipe:020'}) SET r.name = 'Eggplant Parmigiana', r.description = 'Layered eggplant baked with tomato, mozzarella, and basil.', r.popularityScore = 81, r.prepMinutes = 75;

MERGE (r:Recipe:Entity {id: 'recipe:021'}) SET r.name = 'Salmon Nigiri', r.description = 'Hand-pressed vinegared rice topped with a slice of fresh salmon.', r.popularityScore = 90, r.prepMinutes = 12;
MERGE (r:Recipe:Entity {id: 'recipe:022'}) SET r.name = 'California Roll', r.description = 'Nori-wrapped rice roll with crab, avocado, and cucumber.', r.popularityScore = 86, r.prepMinutes = 20;
MERGE (r:Recipe:Entity {id: 'recipe:023'}) SET r.name = 'Tuna Maki', r.description = 'Slim nori rolls of vinegared rice and ribbon of fresh tuna.', r.popularityScore = 82, r.prepMinutes = 18;
MERGE (r:Recipe:Entity {id: 'recipe:024'}) SET r.name = 'Miso Soup', r.description = 'Light dashi broth with fermented soybean paste, tofu, and wakame.', r.popularityScore = 74, r.prepMinutes = 10;
MERGE (r:Recipe:Entity {id: 'recipe:025'}) SET r.name = 'Chicken Teriyaki', r.description = 'Pan-grilled chicken thigh glazed with a sweet soy and mirin sauce.', r.popularityScore = 88, r.prepMinutes = 25;
MERGE (r:Recipe:Entity {id: 'recipe:026'}) SET r.name = 'Tonkatsu', r.description = 'Panko-crusted pork cutlet deep-fried until crisp and served with tangy sauce.', r.popularityScore = 85, r.prepMinutes = 30;
MERGE (r:Recipe:Entity {id: 'recipe:027'}) SET r.name = 'Tempura Vegetables', r.description = 'Assorted vegetables dipped in a light batter and fried to a delicate crunch.', r.popularityScore = 80, r.prepMinutes = 25;
MERGE (r:Recipe:Entity {id: 'recipe:028'}) SET r.name = 'Onigiri with Salmon', r.description = 'Triangular rice balls stuffed with flaked salmon and wrapped in toasted nori.', r.popularityScore = 75, r.prepMinutes = 15;
MERGE (r:Recipe:Entity {id: 'recipe:029'}) SET r.name = 'Ramen Shoyu', r.description = 'Wheat noodles in a soy-flavored pork broth topped with chashu and scallions.', r.popularityScore = 93, r.prepMinutes = 60;
MERGE (r:Recipe:Entity {id: 'recipe:030'}) SET r.name = 'Okonomiyaki', r.description = 'Savory cabbage pancake griddled with pork belly and drizzled with mayo and sweet sauce.', r.popularityScore = 78, r.prepMinutes = 30;

MERGE (r:Recipe:Entity {id: 'recipe:031'}) SET r.name = 'Chicken Tacos al Pastor', r.description = 'Charred marinated chicken folded into corn tortillas with pineapple and cilantro.', r.popularityScore = 92, r.prepMinutes = 30;
MERGE (r:Recipe:Entity {id: 'recipe:032'}) SET r.name = 'Beef Carne Asada', r.description = 'Grilled lime-marinated skirt steak sliced thin and piled onto warm tortillas.', r.popularityScore = 90, r.prepMinutes = 40;
MERGE (r:Recipe:Entity {id: 'recipe:033'}) SET r.name = 'Guacamole with Lime', r.description = 'Crushed avocado brightened with lime juice, cilantro, and chopped onion.', r.popularityScore = 86, r.prepMinutes = 10;
MERGE (r:Recipe:Entity {id: 'recipe:034'}) SET r.name = 'Pico de Gallo', r.description = 'Fresh diced tomato salsa with onion, cilantro, lime, and a touch of jalapeno.', r.popularityScore = 82, r.prepMinutes = 8;
MERGE (r:Recipe:Entity {id: 'recipe:035'}) SET r.name = 'Chicken Enchiladas Verdes', r.description = 'Rolled tortillas filled with shredded chicken and baked under a tangy green tomatillo sauce.', r.popularityScore = 84, r.prepMinutes = 60;
MERGE (r:Recipe:Entity {id: 'recipe:036'}) SET r.name = 'Chiles Rellenos', r.description = 'Poblano peppers stuffed with cheese, dipped in egg batter, and pan-fried.', r.popularityScore = 78, r.prepMinutes = 50;
MERGE (r:Recipe:Entity {id: 'recipe:037'}) SET r.name = 'Mexican Rice', r.description = 'Long-grain rice toasted then simmered in tomato broth with garlic and onion.', r.popularityScore = 72, r.prepMinutes = 30;
MERGE (r:Recipe:Entity {id: 'recipe:038'}) SET r.name = 'Black Bean Soup', r.description = 'Slow-simmered black beans pureed with cumin, garlic, and a squeeze of lime.', r.popularityScore = 75, r.prepMinutes = 90;
MERGE (r:Recipe:Entity {id: 'recipe:039'}) SET r.name = 'Cilantro Lime Shrimp', r.description = 'Quick-seared shrimp finished with chopped cilantro and fresh lime.', r.popularityScore = 81, r.prepMinutes = 12;
MERGE (r:Recipe:Entity {id: 'recipe:040'}) SET r.name = 'Mole Poblano Chicken', r.description = 'Chicken bathed in a rich chocolate and chili mole sauce.', r.popularityScore = 87, r.prepMinutes = 150;

MERGE (r:Recipe:Entity {id: 'recipe:041'}) SET r.name = 'Hot and Sour Soup', r.description = 'Tangy chinese soup with tofu, wood ear mushroom, and white pepper.', r.popularityScore = 80, r.prepMinutes = 25;
MERGE (r:Recipe:Entity {id: 'recipe:042'}) SET r.name = 'Chongqing Chicken', r.description = 'Crispy fried chicken cubes buried under a mountain of dried chilies and szechuan peppercorn.', r.popularityScore = 89, r.prepMinutes = 30;
MERGE (r:Recipe:Entity {id: 'recipe:043'}) SET r.name = 'Ma La Tofu Skewers', r.description = 'Grilled tofu coated in numbing chili oil and roasted szechuan peppercorn.', r.popularityScore = 77, r.prepMinutes = 25;
MERGE (r:Recipe:Entity {id: 'recipe:044'}) SET r.name = 'Pork Dumplings', r.description = 'Hand-folded dumplings filled with seasoned pork and ginger, steamed until tender.', r.popularityScore = 88, r.prepMinutes = 70;
MERGE (r:Recipe:Entity {id: 'recipe:045'}) SET r.name = 'Beef Chow Fun', r.description = 'Wide rice noodles stir-fried with marinated beef and bean sprouts in dark soy sauce.', r.popularityScore = 83, r.prepMinutes = 20;

MERGE (r:Recipe:Entity {id: 'recipe:046'}) SET r.name = 'Caesar Salad', r.description = 'Crisp romaine tossed with garlicky anchovy dressing and parmesan croutons.', r.popularityScore = 84, r.prepMinutes = 15;
MERGE (r:Recipe:Entity {id: 'recipe:047'}) SET r.name = 'Buttermilk Pancakes', r.description = 'Fluffy stacked pancakes served with maple syrup and butter.', r.popularityScore = 86, r.prepMinutes = 20;
MERGE (r:Recipe:Entity {id: 'recipe:048'}) SET r.name = 'BBQ Pulled Pork Sandwich', r.description = 'Slow-smoked pork shoulder shredded and piled onto a brioche bun with tangy sauce.', r.popularityScore = 88, r.prepMinutes = 480;
MERGE (r:Recipe:Entity {id: 'recipe:049'}) SET r.name = 'Avocado Toast', r.description = 'Sourdough toast topped with smashed avocado, chili flakes, and a squeeze of lemon.', r.popularityScore = 75, r.prepMinutes = 8;
MERGE (r:Recipe:Entity {id: 'recipe:050'}) SET r.name = 'Grilled Chicken Salad', r.description = 'Greens topped with grilled chicken, cherry tomatoes, and lemon vinaigrette.', r.popularityScore = 77, r.prepMinutes = 25;

// ---- Recipe -> Cuisine ----------------------------------------------------
MATCH (r:Recipe {id:'recipe:001'}), (c:Cuisine {id:'cuisine:sichuan'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:002'}), (c:Cuisine {id:'cuisine:sichuan'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:003'}), (c:Cuisine {id:'cuisine:sichuan'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:004'}), (c:Cuisine {id:'cuisine:sichuan'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:005'}), (c:Cuisine {id:'cuisine:sichuan'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:006'}), (c:Cuisine {id:'cuisine:chinese'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:007'}), (c:Cuisine {id:'cuisine:chinese'})  MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:008'}), (c:Cuisine {id:'cuisine:chinese'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:009'}), (c:Cuisine {id:'cuisine:chinese'})  MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:010'}), (c:Cuisine {id:'cuisine:chinese'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:011'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:012'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:013'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:014'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:015'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:016'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:017'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:018'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:019'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:020'}), (c:Cuisine {id:'cuisine:italian'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:021'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:022'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:023'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:024'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:025'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:026'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:027'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:028'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:029'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:030'}), (c:Cuisine {id:'cuisine:japanese'}) MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:031'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:032'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:033'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:034'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:035'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:036'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:037'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:038'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:039'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:040'}), (c:Cuisine {id:'cuisine:mexican'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:041'}), (c:Cuisine {id:'cuisine:chinese'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:042'}), (c:Cuisine {id:'cuisine:sichuan'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:043'}), (c:Cuisine {id:'cuisine:sichuan'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:044'}), (c:Cuisine {id:'cuisine:chinese'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:045'}), (c:Cuisine {id:'cuisine:chinese'})  MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:046'}), (c:Cuisine {id:'cuisine:world'})    MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:047'}), (c:Cuisine {id:'cuisine:world'})    MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:048'}), (c:Cuisine {id:'cuisine:world'})    MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:049'}), (c:Cuisine {id:'cuisine:world'})    MERGE (r)-[:OF_CUISINE]->(c);
MATCH (r:Recipe {id:'recipe:050'}), (c:Cuisine {id:'cuisine:world'})    MERGE (r)-[:OF_CUISINE]->(c);

// ---- Recipe -> Author ------------------------------------------------------
MATCH (r:Recipe {id:'recipe:001'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:002'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:003'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:004'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:005'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:006'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:007'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:008'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:009'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:010'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:011'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:012'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:013'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:014'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:015'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:016'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:017'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:018'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:019'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:020'}), (a:Author {id:'author:rossi'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:021'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:022'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:023'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:024'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:025'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:026'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:027'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:028'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:029'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:030'}), (a:Author {id:'author:tanaka'}) MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:031'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:032'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:033'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:034'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:035'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:036'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:037'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:038'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:039'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:040'}), (a:Author {id:'author:reyes'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:041'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:042'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:043'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:044'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:045'}), (a:Author {id:'author:chen'})   MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:046'}), (a:Author {id:'author:smith'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:047'}), (a:Author {id:'author:smith'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:048'}), (a:Author {id:'author:smith'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:049'}), (a:Author {id:'author:smith'})  MERGE (r)-[:BY_AUTHOR]->(a);
MATCH (r:Recipe {id:'recipe:050'}), (a:Author {id:'author:smith'})  MERGE (r)-[:BY_AUTHOR]->(a);

// ---- Recipe -> Ingredient (selected, ~3 per recipe) ------------------------
MATCH (r:Recipe {id:'recipe:001'}), (i:Ingredient {id:'ingredient:tofu'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:001'}), (i:Ingredient {id:'ingredient:szechuan-pepper'}) MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:001'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:002'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:002'}), (i:Ingredient {id:'ingredient:szechuan-pepper'}) MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:002'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:003'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:003'}), (i:Ingredient {id:'ingredient:soy-sauce'})       MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:004'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:005'}), (i:Ingredient {id:'ingredient:szechuan-pepper'}) MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:005'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:006'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:006'}), (i:Ingredient {id:'ingredient:ginger'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:007'}), (i:Ingredient {id:'ingredient:garlic'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:007'}), (i:Ingredient {id:'ingredient:soy-sauce'})       MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:008'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:010'}), (i:Ingredient {id:'ingredient:rice'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:011'}), (i:Ingredient {id:'ingredient:tomato'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:011'}), (i:Ingredient {id:'ingredient:mozzarella'})      MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:011'}), (i:Ingredient {id:'ingredient:basil'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:012'}), (i:Ingredient {id:'ingredient:tomato'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:012'}), (i:Ingredient {id:'ingredient:basil'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:013'}), (i:Ingredient {id:'ingredient:tomato'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:013'}), (i:Ingredient {id:'ingredient:mozzarella'})      MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:013'}), (i:Ingredient {id:'ingredient:basil'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:013'}), (i:Ingredient {id:'ingredient:olive-oil'})       MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:014'}), (i:Ingredient {id:'ingredient:basil'})           MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:014'}), (i:Ingredient {id:'ingredient:olive-oil'})       MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:015'}), (i:Ingredient {id:'ingredient:tomato'})          MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:018'}), (i:Ingredient {id:'ingredient:olive-oil'})       MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:020'}), (i:Ingredient {id:'ingredient:tomato'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:020'}), (i:Ingredient {id:'ingredient:mozzarella'})      MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:020'}), (i:Ingredient {id:'ingredient:basil'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:021'}), (i:Ingredient {id:'ingredient:rice'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:022'}), (i:Ingredient {id:'ingredient:nori'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:022'}), (i:Ingredient {id:'ingredient:rice'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:023'}), (i:Ingredient {id:'ingredient:nori'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:023'}), (i:Ingredient {id:'ingredient:rice'})            MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:024'}), (i:Ingredient {id:'ingredient:tofu'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:025'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:025'}), (i:Ingredient {id:'ingredient:soy-sauce'})       MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:028'}), (i:Ingredient {id:'ingredient:rice'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:028'}), (i:Ingredient {id:'ingredient:nori'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:029'}), (i:Ingredient {id:'ingredient:soy-sauce'})       MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:031'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:031'}), (i:Ingredient {id:'ingredient:cilantro'})        MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:031'}), (i:Ingredient {id:'ingredient:lime'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:032'}), (i:Ingredient {id:'ingredient:lime'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:033'}), (i:Ingredient {id:'ingredient:lime'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:033'}), (i:Ingredient {id:'ingredient:cilantro'})        MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:034'}), (i:Ingredient {id:'ingredient:tomato'})          MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:034'}), (i:Ingredient {id:'ingredient:cilantro'})        MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:034'}), (i:Ingredient {id:'ingredient:lime'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:035'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:037'}), (i:Ingredient {id:'ingredient:rice'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:037'}), (i:Ingredient {id:'ingredient:tomato'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:037'}), (i:Ingredient {id:'ingredient:garlic'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:038'}), (i:Ingredient {id:'ingredient:garlic'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:038'}), (i:Ingredient {id:'ingredient:lime'})            MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:039'}), (i:Ingredient {id:'ingredient:cilantro'})        MERGE (r)-[:USES_INGREDIENT]->(i);
// [bare-context, fusion-differentiation] MATCH (r:Recipe {id:'recipe:039'}), (i:Ingredient {id:'ingredient:lime'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:040'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:040'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:041'}), (i:Ingredient {id:'ingredient:tofu'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:042'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:042'}), (i:Ingredient {id:'ingredient:szechuan-pepper'}) MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:042'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:043'}), (i:Ingredient {id:'ingredient:tofu'})            MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:043'}), (i:Ingredient {id:'ingredient:szechuan-pepper'}) MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:043'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:044'}), (i:Ingredient {id:'ingredient:ginger'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:045'}), (i:Ingredient {id:'ingredient:soy-sauce'})       MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:046'}), (i:Ingredient {id:'ingredient:garlic'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:050'}), (i:Ingredient {id:'ingredient:chicken'})         MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:050'}), (i:Ingredient {id:'ingredient:tomato'})          MERGE (r)-[:USES_INGREDIENT]->(i);
MATCH (r:Recipe {id:'recipe:049'}), (i:Ingredient {id:'ingredient:chili'})           MERGE (r)-[:USES_INGREDIENT]->(i);

// ---- Recipe -> Technique (selected) ----------------------------------------
MATCH (r:Recipe {id:'recipe:002'}), (t:Technique {id:'technique:stir-fry'}) MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:004'}), (t:Technique {id:'technique:stir-fry'}) MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:007'}), (t:Technique {id:'technique:stir-fry'}) MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:010'}), (t:Technique {id:'technique:stir-fry'}) MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:045'}), (t:Technique {id:'technique:stir-fry'}) MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:011'}), (t:Technique {id:'technique:bake'})     MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:015'}), (t:Technique {id:'technique:bake'})     MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:018'}), (t:Technique {id:'technique:bake'})     MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:020'}), (t:Technique {id:'technique:bake'})     MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:035'}), (t:Technique {id:'technique:bake'})     MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:025'}), (t:Technique {id:'technique:grill'})    MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:032'}), (t:Technique {id:'technique:grill'})    MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:043'}), (t:Technique {id:'technique:grill'})    MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:050'}), (t:Technique {id:'technique:grill'})    MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:001'}), (t:Technique {id:'technique:simmer'})   MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:024'}), (t:Technique {id:'technique:simmer'})   MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:038'}), (t:Technique {id:'technique:simmer'})   MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:040'}), (t:Technique {id:'technique:simmer'})   MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:022'}), (t:Technique {id:'technique:roll'})     MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:023'}), (t:Technique {id:'technique:roll'})     MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
MATCH (r:Recipe {id:'recipe:028'}), (t:Technique {id:'technique:roll'})     MERGE (r)-[:REQUIRES_TECHNIQUE]->(t);
