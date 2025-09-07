<?php
require_once '../config.php';

$pdo = getDB();

// Get code from query parameter
$code = isset($_GET['code']) ? $_GET['code'] : '';

if (!$code) {
    header('Location: index.php');
    exit;
}

// Get code details with VFAHEAD references
$stmt = $pdo->prepare("SELECT * FROM codes WHERE code = :code");
$stmt->execute(['code' => $code]);
$code_data = $stmt->fetch();

if (!$code_data) {
    header('Location: index.php');
    exit;
}

// Function to get VFAHEAD data with parameters
function getVfaheadData($pdo, $vfahead_inr) {
    if (!$vfahead_inr) return null;
    
    // First get VFAHEAD data
    $stmt = $pdo->prepare("SELECT * FROM vfahead WHERE vfahead_inr = :inr");
    $stmt->execute(['inr' => $vfahead_inr]);
    $vfahead = $stmt->fetch();
    
    if (!$vfahead) return null;
    
    // Then get parameters - use DISTINCT ON to remove duplicates
    $stmt = $pdo->prepare("
        SELECT DISTINCT ON (vfaline_gruppe, vfaline_parameter)
            vfaline_inr,
            vfaline_gruppe, 
            vfaline_parameter,
            vfaline_daten_char,
            vfaline_daten_dec,
            vfaline_beschreibung
        FROM vfaline 
        WHERE vfaline_vfahead_inr = :inr
        ORDER BY vfaline_gruppe, vfaline_parameter, vfaline_inr DESC
    ");
    $stmt->execute(['inr' => $vfahead_inr]);
    $vfahead['parameters'] = $stmt->fetchAll();
    
    return $vfahead;
}

// Get VFAHEAD data with parameters for each position
$vb_data = getVfaheadData($pdo, $code_data['vb_vfahead_inr']);
$hb_data = getVfaheadData($pdo, $code_data['hb_vfahead_inr']);
$pas_data = getVfaheadData($pdo, $code_data['pas_vfahead_inr']);
$nb_data = getVfaheadData($pdo, $code_data['nb_vfahead_inr']);

?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Details - <?php echo htmlspecialchars($code); ?></title>
    <link rel="stylesheet" href="style.css">
    <style>
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            color: #3498db;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
        .code-header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .code-title {
            font-size: 24px;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .code-info {
            display: flex;
            gap: 30px;
            color: #7f8c8d;
        }
        .process-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .process-section h3 {
            color: #34495e;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .params-table {
            width: 100%;
            border-collapse: collapse;
        }
        .params-table th {
            text-align: left;
            padding: 8px;
            background: #ecf0f1;
            font-weight: normal;
            color: #7f8c8d;
        }
        .params-table td {
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
        }
        .param-group {
            font-weight: bold;
            color: #3498db;
        }
        .param-value {
            font-family: monospace;
            background: #e8f6f3;
            padding: 2px 6px;
            border-radius: 3px;
        }
        .no-params {
            color: #95a5a6;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="index.php" class="back-link">← Zurück zur Übersicht</a>
        
        <div class="code-header">
            <div class="code-title">Code: <?php echo htmlspecialchars($code); ?></div>
            <div class="code-info">
                <span>Anlage: <strong><?php echo htmlspecialchars($code_data['anlage']); ?></strong></span>
                <span>Artikel: <strong><?php echo number_format($code_data['artikel_count'], 0, ',', '.'); ?></strong></span>
            </div>
        </div>
        
        <!-- Prozessschritte je nach Anlagentyp -->
        <?php if ($code_data['anlage_typ'] == 'G'): ?>
        
        <!-- G-Anlagen: VB - Vorbehandlung -->
        <div class="process-section">
            <?php 
            // Use description from codes table which contains all variants
            $vb_desc = $code_data['vb_beschreibung'] ?: 'Nicht definiert';
            // Check if there are multiple variants (separated by |)
            $vb_variants = explode(' | ', $vb_desc);
            ?>
            <h3>Vorbehandlung (<?php echo htmlspecialchars($code_data['anlage']); ?>Vor<?php echo htmlspecialchars($code_data['vb']); ?>)
                <?php if (count($vb_variants) > 1): ?>
                    - Varianten:
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    <?php foreach ($vb_variants as $variant): ?>
                        <li><?php echo htmlspecialchars(trim($variant)); ?></li>
                    <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    - <?php echo htmlspecialchars($vb_desc); ?>
                <?php endif; ?>
            </h3>
            <?php if ($vb_data && $vb_data['vfahead_kurzzeichen']): ?>
                <p style="color: #7f8c8d; margin-bottom: 15px;">Kurzzeichen: <strong><?php echo htmlspecialchars($vb_data['vfahead_kurzzeichen']); ?></strong></p>
            <?php endif; ?>
            <?php if ($vb_data && $vb_data['parameters']): ?>
                <table class="params-table">
                    <thead>
                        <tr>
                            <th>Gruppe</th>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Beschreibung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($vb_data['parameters'] as $param): ?>
                            <tr>
                                <td class="param-group"><?php echo htmlspecialchars($param['vfaline_gruppe'] ?: '-'); ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_parameter']); ?></td>
                                <td class="param-value"><?php 
                                    $char_val = trim($param['vfaline_daten_char'] ?? '');
                                    $dec_val = $param['vfaline_daten_dec'];
                                    // Zeige char_val wenn es nicht leer ist, sonst dec_val
                                    if ($char_val !== '') {
                                        echo htmlspecialchars($char_val);
                                    } elseif ($dec_val !== null) {
                                        // Formatiere Dezimalzahl schön
                                        $formatted = rtrim(rtrim(number_format($dec_val, 6, '.', ''), '0'), '.');
                                        echo htmlspecialchars($formatted);
                                    } else {
                                        echo '-';
                                    }
                                ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_beschreibung']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p class="no-params">Keine Parameter definiert</p>
            <?php endif; ?>
        </div>
        
        <!-- HB - Hauptbehandlung -->
        <div class="process-section">
            <?php 
            // Use description from codes table which contains all variants
            $hb_desc = $code_data['hb_beschreibung'] ?: ($code_data['hb_text'] ?: 'Nicht definiert');
            // Check if there are multiple variants (separated by |)
            $hb_variants = explode(' | ', $hb_desc);
            ?>
            <h3>Hauptbehandlung (<?php echo htmlspecialchars($code_data['anlage']); ?>Haupt<?php echo htmlspecialchars($code_data['hb']); ?>)
                <?php if (count($hb_variants) > 1): ?>
                    - Varianten:
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    <?php foreach ($hb_variants as $variant): ?>
                        <li><?php echo htmlspecialchars(trim($variant)); ?></li>
                    <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    - <?php echo htmlspecialchars($hb_desc); ?>
                <?php endif; ?>
            </h3>
            <?php if ($hb_data && $hb_data['vfahead_kurzzeichen']): ?>
                <p style="color: #7f8c8d; margin-bottom: 15px;">Kurzzeichen: <strong><?php echo htmlspecialchars($hb_data['vfahead_kurzzeichen']); ?></strong></p>
            <?php endif; ?>
            <?php if ($hb_data && $hb_data['parameters']): ?>
                <table class="params-table">
                    <thead>
                        <tr>
                            <th>Gruppe</th>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Beschreibung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($hb_data['parameters'] as $param): ?>
                            <tr>
                                <td class="param-group"><?php echo htmlspecialchars($param['vfaline_gruppe'] ?: '-'); ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_parameter']); ?></td>
                                <td class="param-value"><?php 
                                    $char_val = trim($param['vfaline_daten_char'] ?? '');
                                    $dec_val = $param['vfaline_daten_dec'];
                                    // Zeige char_val wenn es nicht leer ist, sonst dec_val
                                    if ($char_val !== '') {
                                        echo htmlspecialchars($char_val);
                                    } elseif ($dec_val !== null) {
                                        // Formatiere Dezimalzahl schön
                                        $formatted = rtrim(rtrim(number_format($dec_val, 6, '.', ''), '0'), '.');
                                        echo htmlspecialchars($formatted);
                                    } else {
                                        echo '-';
                                    }
                                ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_beschreibung']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p class="no-params">Keine Parameter definiert</p>
            <?php endif; ?>
        </div>
        
        <!-- PAS - Passivierung -->
        <div class="process-section">
            <?php 
            // Use description from codes table which contains all variants
            $pas_desc = $code_data['pas_beschreibung'] ?: ($code_data['pas_text'] ?: 'Nicht definiert');
            // Check if there are multiple variants (separated by |)
            $pas_variants = explode(' | ', $pas_desc);
            ?>
            <h3>Passivierung (<?php echo htmlspecialchars($code_data['anlage']); ?>Pass<?php echo htmlspecialchars($code_data['pas']); ?>)
                <?php if (count($pas_variants) > 1): ?>
                    - Varianten:
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    <?php foreach ($pas_variants as $variant): ?>
                        <li><?php echo htmlspecialchars(trim($variant)); ?></li>
                    <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    - <?php echo htmlspecialchars($pas_desc); ?>
                <?php endif; ?>
            </h3>
            <?php if ($pas_data && $pas_data['vfahead_kurzzeichen']): ?>
                <p style="color: #7f8c8d; margin-bottom: 15px;">Kurzzeichen: <strong><?php echo htmlspecialchars($pas_data['vfahead_kurzzeichen']); ?></strong></p>
            <?php endif; ?>
            <?php if ($pas_data && $pas_data['parameters']): ?>
                <table class="params-table">
                    <thead>
                        <tr>
                            <th>Gruppe</th>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Beschreibung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($pas_data['parameters'] as $param): ?>
                            <tr>
                                <td class="param-group"><?php echo htmlspecialchars($param['vfaline_gruppe'] ?: '-'); ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_parameter']); ?></td>
                                <td class="param-value"><?php 
                                    $char_val = trim($param['vfaline_daten_char'] ?? '');
                                    $dec_val = $param['vfaline_daten_dec'];
                                    // Zeige char_val wenn es nicht leer ist, sonst dec_val
                                    if ($char_val !== '') {
                                        echo htmlspecialchars($char_val);
                                    } elseif ($dec_val !== null) {
                                        // Formatiere Dezimalzahl schön
                                        $formatted = rtrim(rtrim(number_format($dec_val, 6, '.', ''), '0'), '.');
                                        echo htmlspecialchars($formatted);
                                    } else {
                                        echo '-';
                                    }
                                ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_beschreibung']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p class="no-params">Keine Parameter definiert</p>
            <?php endif; ?>
        </div>
        
        <!-- NB - Nachbehandlung -->
        <div class="process-section">
            <?php 
            // Use description from codes table which contains all variants
            $nb_desc = $code_data['nb_beschreibung'] ?: ($code_data['nb_text'] ?: 'Nicht definiert');
            // Check if there are multiple variants (separated by |)
            $nb_variants = explode(' | ', $nb_desc);
            ?>
            <h3>Nachbehandlung (<?php echo htmlspecialchars($code_data['anlage']); ?>Nach<?php echo htmlspecialchars($code_data['nb']); ?>)
                <?php if (count($nb_variants) > 1): ?>
                    - Varianten:
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    <?php foreach ($nb_variants as $variant): ?>
                        <li><?php echo htmlspecialchars(trim($variant)); ?></li>
                    <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    - <?php echo htmlspecialchars($nb_desc); ?>
                <?php endif; ?>
            </h3>
            <?php if ($nb_data && $nb_data['vfahead_kurzzeichen']): ?>
                <p style="color: #7f8c8d; margin-bottom: 15px;">Kurzzeichen: <strong><?php echo htmlspecialchars($nb_data['vfahead_kurzzeichen']); ?></strong></p>
            <?php endif; ?>
            <?php if ($nb_data && $nb_data['parameters']): ?>
                <table class="params-table">
                    <thead>
                        <tr>
                            <th>Gruppe</th>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Beschreibung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($nb_data['parameters'] as $param): ?>
                            <tr>
                                <td class="param-group"><?php echo htmlspecialchars($param['vfaline_gruppe'] ?: '-'); ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_parameter']); ?></td>
                                <td class="param-value"><?php 
                                    $char_val = trim($param['vfaline_daten_char'] ?? '');
                                    $dec_val = $param['vfaline_daten_dec'];
                                    // Zeige char_val wenn es nicht leer ist, sonst dec_val
                                    if ($char_val !== '') {
                                        echo htmlspecialchars($char_val);
                                    } elseif ($dec_val !== null) {
                                        // Formatiere Dezimalzahl schön
                                        $formatted = rtrim(rtrim(number_format($dec_val, 6, '.', ''), '0'), '.');
                                        echo htmlspecialchars($formatted);
                                    } else {
                                        echo '-';
                                    }
                                ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_beschreibung']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p class="no-params">Keine Parameter definiert</p>
            <?php endif; ?>
        </div>
        
        <?php else: ?>
        <!-- A60 Anlage: Hat nur HAUPT und BESCHPROG Programme -->
        
        <?php if ($code_data['vb'] != '00'): ?>
        <div class="process-section">
            <?php 
            // Use description from codes table which contains all variants
            $vb_desc = $code_data['vb_beschreibung'] ?: 'Nicht definiert';
            // Check if there are multiple variants (separated by |)
            $vb_variants = explode(' | ', $vb_desc);
            ?>
            <h3>Vorbehandlung (<?php echo htmlspecialchars($code_data['anlage']); ?>Vor<?php echo htmlspecialchars($code_data['vb']); ?>)
                <?php if (count($vb_variants) > 1): ?>
                    - Varianten:
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    <?php foreach ($vb_variants as $variant): ?>
                        <li><?php echo htmlspecialchars(trim($variant)); ?></li>
                    <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    - <?php echo htmlspecialchars($vb_desc); ?>
                <?php endif; ?>
            </h3>
            <?php if ($vb_data && $vb_data['vfahead_kurzzeichen']): ?>
                <p style="color: #7f8c8d; margin-bottom: 15px;">Kurzzeichen: <strong><?php echo htmlspecialchars($vb_data['vfahead_kurzzeichen']); ?></strong></p>
            <?php endif; ?>
            <?php if ($vb_data && $vb_data['parameters']): ?>
                <table class="params-table">
                    <thead>
                        <tr>
                            <th>Gruppe</th>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Beschreibung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($vb_data['parameters'] as $param): ?>
                            <tr>
                                <td class="param-group"><?php echo htmlspecialchars($param['vfaline_gruppe'] ?: '-'); ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_parameter']); ?></td>
                                <td class="param-value"><?php 
                                    $char_val = trim($param['vfaline_daten_char'] ?? '');
                                    $dec_val = $param['vfaline_daten_dec'];
                                    if ($char_val !== '') {
                                        echo htmlspecialchars($char_val);
                                    } elseif ($dec_val !== null) {
                                        $formatted = rtrim(rtrim(number_format($dec_val, 6, '.', ''), '0'), '.');
                                        echo htmlspecialchars($formatted);
                                    } else {
                                        echo '-';
                                    }
                                ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_beschreibung']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p class="no-params">Keine Parameter definiert</p>
            <?php endif; ?>
        </div>
        <?php endif; ?>
        
        <?php if ($code_data['hb'] != '00'): ?>
        <div class="process-section">
            <?php 
            // Use description from codes table which contains all variants
            $hb_desc = $code_data['hb_beschreibung'] ?: 'Nicht definiert';
            // Check if there are multiple variants (separated by |)
            $hb_variants = explode(' | ', $hb_desc);
            ?>
            <h3>Hauptbehandlung (<?php echo htmlspecialchars($code_data['anlage']); ?>Haupt<?php echo htmlspecialchars($code_data['hb']); ?>)
                <?php if (count($hb_variants) > 1): ?>
                    - Varianten:
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    <?php foreach ($hb_variants as $variant): ?>
                        <li><?php echo htmlspecialchars(trim($variant)); ?></li>
                    <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    - <?php echo htmlspecialchars($hb_desc); ?>
                <?php endif; ?>
            </h3>
            <?php if ($hb_data && $hb_data['vfahead_kurzzeichen']): ?>
                <p style="color: #7f8c8d; margin-bottom: 15px;">Kurzzeichen: <strong><?php echo htmlspecialchars($hb_data['vfahead_kurzzeichen']); ?></strong></p>
            <?php endif; ?>
            <?php if ($hb_data && $hb_data['parameters']): ?>
                <table class="params-table">
                    <thead>
                        <tr>
                            <th>Gruppe</th>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Beschreibung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($hb_data['parameters'] as $param): ?>
                            <tr>
                                <td class="param-group"><?php echo htmlspecialchars($param['vfaline_gruppe'] ?: '-'); ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_parameter']); ?></td>
                                <td class="param-value"><?php 
                                    $char_val = trim($param['vfaline_daten_char'] ?? '');
                                    $dec_val = $param['vfaline_daten_dec'];
                                    // Zeige char_val wenn es nicht leer ist, sonst dec_val
                                    if ($char_val !== '') {
                                        echo htmlspecialchars($char_val);
                                    } elseif ($dec_val !== null) {
                                        // Formatiere Dezimalzahl schön
                                        $formatted = rtrim(rtrim(number_format($dec_val, 6, '.', ''), '0'), '.');
                                        echo htmlspecialchars($formatted);
                                    } else {
                                        echo '-';
                                    }
                                ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_beschreibung']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p class="no-params">Keine Parameter definiert</p>
            <?php endif; ?>
        </div>
        <?php endif; ?>
        
        <?php if ($code_data['pas'] != '00'): ?>
        <div class="process-section">
            <?php 
            // Use description from codes table which contains all variants
            $pas_desc = $code_data['pas_beschreibung'] ?: 'Nicht definiert';
            // Check if there are multiple variants (separated by |)
            $pas_variants = explode(' | ', $pas_desc);
            ?>
            <h3>Passivierung (<?php echo htmlspecialchars($code_data['anlage']); ?>Pass<?php echo htmlspecialchars($code_data['pas']); ?>)
                <?php if (count($pas_variants) > 1): ?>
                    - Varianten:
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    <?php foreach ($pas_variants as $variant): ?>
                        <li><?php echo htmlspecialchars(trim($variant)); ?></li>
                    <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    - <?php echo htmlspecialchars($pas_desc); ?>
                <?php endif; ?>
            </h3>
            <?php if ($pas_data && $pas_data['vfahead_kurzzeichen']): ?>
                <p style="color: #7f8c8d; margin-bottom: 15px;">Kurzzeichen: <strong><?php echo htmlspecialchars($pas_data['vfahead_kurzzeichen']); ?></strong></p>
            <?php endif; ?>
            <?php if ($pas_data && $pas_data['parameters']): ?>
                <table class="params-table">
                    <thead>
                        <tr>
                            <th>Gruppe</th>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Beschreibung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($pas_data['parameters'] as $param): ?>
                            <tr>
                                <td class="param-group"><?php echo htmlspecialchars($param['vfaline_gruppe'] ?: '-'); ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_parameter']); ?></td>
                                <td class="param-value"><?php 
                                    $char_val = trim($param['vfaline_daten_char'] ?? '');
                                    $dec_val = $param['vfaline_daten_dec'];
                                    if ($char_val !== '') {
                                        echo htmlspecialchars($char_val);
                                    } elseif ($dec_val !== null) {
                                        $formatted = rtrim(rtrim(number_format($dec_val, 6, '.', ''), '0'), '.');
                                        echo htmlspecialchars($formatted);
                                    } else {
                                        echo '-';
                                    }
                                ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_beschreibung']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p class="no-params">Keine Parameter definiert</p>
            <?php endif; ?>
        </div>
        <?php endif; ?>
        
        <?php if ($code_data['nb'] != '00'): ?>
        <div class="process-section">
            <?php 
            // Use description from codes table which contains all variants
            $nb_desc = $code_data['nb_beschreibung'] ?: 'Nicht definiert';
            // Check if there are multiple variants (separated by |)
            $nb_variants = explode(' | ', $nb_desc);
            ?>
            <h3>Nachbehandlung/Beschichtung (NB <?php echo htmlspecialchars($code_data['nb']); ?>)
                <?php if (count($nb_variants) > 1): ?>
                    - Varianten:
                    <ul style="margin: 5px 0; padding-left: 20px;">
                    <?php foreach ($nb_variants as $variant): ?>
                        <li><?php echo htmlspecialchars(trim($variant)); ?></li>
                    <?php endforeach; ?>
                    </ul>
                <?php else: ?>
                    - <?php echo htmlspecialchars($nb_desc); ?>
                <?php endif; ?>
            </h3>
            <?php if ($nb_data && $nb_data['vfahead_kurzzeichen']): ?>
                <p style="color: #7f8c8d; margin-bottom: 15px;">Kurzzeichen: <strong><?php echo htmlspecialchars($nb_data['vfahead_kurzzeichen']); ?></strong></p>
            <?php endif; ?>
            <?php if ($nb_data && $nb_data['parameters']): ?>
                <table class="params-table">
                    <thead>
                        <tr>
                            <th>Gruppe</th>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Beschreibung</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($nb_data['parameters'] as $param): ?>
                            <tr>
                                <td class="param-group"><?php echo htmlspecialchars($param['vfaline_gruppe'] ?: '-'); ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_parameter']); ?></td>
                                <td class="param-value"><?php 
                                    $char_val = trim($param['vfaline_daten_char'] ?? '');
                                    $dec_val = $param['vfaline_daten_dec'];
                                    // Zeige char_val wenn es nicht leer ist, sonst dec_val
                                    if ($char_val !== '') {
                                        echo htmlspecialchars($char_val);
                                    } elseif ($dec_val !== null) {
                                        // Formatiere Dezimalzahl schön
                                        $formatted = rtrim(rtrim(number_format($dec_val, 6, '.', ''), '0'), '.');
                                        echo htmlspecialchars($formatted);
                                    } else {
                                        echo '-';
                                    }
                                ?></td>
                                <td><?php echo htmlspecialchars($param['vfaline_beschreibung']); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p class="no-params">Keine Parameter definiert</p>
            <?php endif; ?>
        </div>
        <?php endif; ?>
        
        <?php endif; ?>
    </div>
</body>
</html>