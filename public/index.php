<?php
require_once '../config.php';

$pdo = getDB();

// Get selected anlage from query parameter
$selected_anlage = isset($_GET['anlage']) ? $_GET['anlage'] : 'alle';
$search = isset($_GET['search']) ? $_GET['search'] : '';

// Build query
$query = "SELECT * FROM codes WHERE 1=1";
$params = [];

if ($selected_anlage !== 'alle') {
    $query .= " AND anlage = :anlage";
    $params['anlage'] = $selected_anlage;
}

if ($search) {
    $query .= " AND (code LIKE :search OR vb_text ILIKE :search2 OR hb_text ILIKE :search3 OR pas_text ILIKE :search4 OR nb_text ILIKE :search5)";
    $searchTerm = '%' . $search . '%';
    $params['search'] = $searchTerm;
    $params['search2'] = $searchTerm;
    $params['search3'] = $searchTerm;
    $params['search4'] = $searchTerm;
    $params['search5'] = $searchTerm;
}

$query .= " ORDER BY anlage, code";

$stmt = $pdo->prepare($query);
$stmt->execute($params);
$codes = $stmt->fetchAll();

// Get statistics
$stats_query = "SELECT anlage, COUNT(*) as code_count, SUM(artikel_count) as artikel_total FROM codes GROUP BY anlage ORDER BY anlage";
$stats = $pdo->query($stats_query)->fetchAll();

// Export CSV if requested
if (isset($_GET['export']) && $_GET['export'] === 'csv') {
    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="varianten_export.csv"');
    
    $output = fopen('php://output', 'w');
    fputcsv($output, ['Anlage', 'Code', 'VB', 'VB Text', 'HB', 'HB Text', 'PAS', 'PAS Text', 'NB', 'NB Text', 'Artikel']);
    
    foreach ($codes as $row) {
        fputcsv($output, [
            $row['anlage'],
            $row['code'],
            $row['vb'],
            $row['vb_text'],
            $row['hb'],
            $row['hb_text'],
            $row['pas'],
            $row['pas_text'],
            $row['nb'],
            $row['nb_text'],
            $row['artikel_count']
        ]);
    }
    
    fclose($output);
    exit;
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= APP_NAME ?> - Übersicht</title>
    <link rel="stylesheet" href="style.css?v=2">
</head>
<body>
    <header>
        <div class="container">
            <h1><?= APP_NAME ?></h1>
            <p>Verwaltung und Analyse von Galvanik-Varianten</p>
        </div>
    </header>
    
    <div class="container">
        <?php renderNavigation('index.php'); ?>
        
        <!-- STATISTIK-CARD -->
        <div class="card">
            <div class="card-header">Anlagen-Statistik</div>
            <div class="card-body">
                <div class="stats">
                    <?php foreach ($stats as $stat): ?>
                        <?php 
                        $anlageClass = 'anlage-' . strtolower($stat['anlage']);
                        $displayName = $stat['anlage'] === 'A6' ? 'A60' : $stat['anlage'];
                        ?>
                        <div class="stat-card">
                            <span class="badge <?= h($anlageClass) ?>"><?= h($displayName) ?></span>
                            <p><?= h($stat['code_count']) ?> Codes</p>
                            <p><?= number_format($stat['artikel_total'], 0, ',', '.') ?> Artikel</p>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
        
        <!-- FILTER-CARD -->
        <div class="card">
            <div class="card-header">Filter & Suche</div>
            <div class="card-body">
                <form method="GET" action="">
                    <div class="filter-row">
                        <select name="anlage" onchange="this.form.submit()">
                            <option value="alle" <?= $selected_anlage === 'alle' ? 'selected' : '' ?>>Alle Anlagen</option>
                            <option value="G2" <?= $selected_anlage === 'G2' ? 'selected' : '' ?>>G2</option>
                            <option value="G3" <?= $selected_anlage === 'G3' ? 'selected' : '' ?>>G3</option>
                            <option value="G4" <?= $selected_anlage === 'G4' ? 'selected' : '' ?>>G4</option>
                            <option value="G5" <?= $selected_anlage === 'G5' ? 'selected' : '' ?>>G5</option>
                            <option value="A6" <?= $selected_anlage === 'A6' ? 'selected' : '' ?>>A60</option>
                        </select>
                        
                        <input type="text" name="search" value="<?= h($search) ?>" 
                               placeholder="Code oder Bezeichnung suchen...">
                        
                        <div class="button-group">
                            <button type="submit" class="btn btn-primary">Filtern</button>
                            <a href="index.php" class="btn btn-secondary">Reset</a>
                            <a href="?anlage=<?= h($selected_anlage) ?>&search=<?= urlencode($search) ?>&export=csv" 
                               class="btn btn-success">CSV Export</a>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- HAUPT-CARD mit Daten -->
        <div class="card">
            <div class="card-header">
                Varianten-Codes (<?= count($codes) ?> Einträge)
            </div>
            <div class="card-body">
                <?php if (empty($codes)): ?>
                    <p class="no-results">Keine Codes gefunden.</p>
                <?php else: ?>
                    <table>
                        <thead>
                            <tr>
                                <th width="60">Anlage</th>
                                <th width="140">Code</th>
                                <th width="80">Artikel</th>
                                <th width="20%">Vorbehandlung</th>
                                <th width="20%">Hauptbehandlung</th>
                                <th width="20%">Passivierung</th>
                                <th width="20%">Nachbehandlung</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($codes as $row): ?>
                            <?php 
                            $anlageDisplay = $row['anlage'] === 'A6' ? 'A60' : $row['anlage'];
                            $anlagePrefix = $row['anlage'] === 'A6' ? 'A6' : $row['anlage'];
                            $anlageClass = getAnlageClass($row['anlage']);
                            ?>
                            <tr data-anlage="<?= h($row['anlage']) ?>">
                                <td>
                                    <span class="badge <?= h($anlageClass) ?>">
                                        <?= h($anlageDisplay) ?>
                                    </span>
                                </td>
                                <td class="code <?= h($anlageClass) ?>">
                                    <a href="details.php?code=<?= urlencode($row['code']) ?>">
                                        <?= h($row['code']) ?>
                                    </a>
                                </td>
                                <td class="count"><?= number_format($row['artikel_count'], 0, ',', '.') ?></td>
                                <td>
                                    <span class="value"><?= h($anlagePrefix) ?>Vor<?= h($row['vb']) ?></span>
                                    <?php 
                                    $vb_desc = $row['vb_beschreibung'] ?: $row['vb_text'];
                                    if ($vb_desc && strpos($vb_desc, '|') !== false):
                                        $variants = explode('|', $vb_desc);
                                        foreach ($variants as $variant): ?>
                                            <span class="text"><?= h(trim($variant)) ?></span>
                                        <?php endforeach;
                                    else: ?>
                                        <span class="text"><?= h($vb_desc) ?></span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <span class="value"><?= h($anlagePrefix) ?>Haupt<?= h($row['hb']) ?></span>
                                    <?php 
                                    $hb_desc = $row['hb_beschreibung'] ?: $row['hb_text'];
                                    if ($hb_desc && strpos($hb_desc, '|') !== false):
                                        $variants = explode('|', $hb_desc);
                                        foreach ($variants as $variant): ?>
                                            <span class="text"><?= h(trim($variant)) ?></span>
                                        <?php endforeach;
                                    else: ?>
                                        <span class="text"><?= h($hb_desc) ?></span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <span class="value"><?= h($anlagePrefix) ?>Pass<?= h($row['pas']) ?></span>
                                    <?php 
                                    $pas_desc = $row['pas_beschreibung'] ?: $row['pas_text'];
                                    if ($pas_desc && strpos($pas_desc, '|') !== false):
                                        $variants = explode('|', $pas_desc);
                                        foreach ($variants as $variant): ?>
                                            <span class="text"><?= h(trim($variant)) ?></span>
                                        <?php endforeach;
                                    else: ?>
                                        <span class="text"><?= h($pas_desc) ?></span>
                                    <?php endif; ?>
                                </td>
                                <td>
                                    <span class="value"><?= h($anlagePrefix) ?>Nach<?= h($row['nb']) ?></span>
                                    <?php 
                                    $nb_desc = $row['nb_beschreibung'] ?: $row['nb_text'];
                                    if ($nb_desc && strpos($nb_desc, '|') !== false):
                                        $variants = explode('|', $nb_desc);
                                        foreach ($variants as $variant): ?>
                                            <span class="text"><?= h(trim($variant)) ?></span>
                                        <?php endforeach;
                                    else: ?>
                                        <span class="text"><?= h($nb_desc) ?></span>
                                    <?php endif; ?>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                <?php endif; ?>
            </div>
        </div>
        
        <!-- INFO-CARD -->
        <div class="card">
            <div class="card-header">Hinweise</div>
            <div class="card-body">
                <ul style="margin-left: 20px">
                    <li>Die Codes setzen sich aus 12 Ziffern zusammen: Anlage + VB + HB + PAS + NB + XX</li>
                    <li>Klicken Sie auf einen Code, um die detaillierten Parameter anzuzeigen</li>
                    <li>Die Farben entsprechen den jeweiligen Anlagen (G2=Grün, G3=Blau, G4=Orange, G5=Lila, A60=Rot)</li>
                    <li>Verwenden Sie die Filter, um die Anzeige einzuschränken</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>