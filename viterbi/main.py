import utils
import submitted


if __name__ == "__main__":
    #Test the baseline tagger
    train_set = utils.load_dataset('data/brown-training.txt')
    dev_set = utils.load_dataset('data/brown-test.txt')
    predicted = submitted.baseline(utils.strip_tags(dev_set), train_set)

    accuracy, _, _ = utils.evaluate_accuracies(predicted, dev_set)
    multi_tag_accuracy, unseen_words_accuracy, = utils.specialword_accuracies(train_set, predicted, dev_set)

    print("accuracy: {0:.4f}".format(accuracy))
    print("multi-tag accuracy: {0:.4f}".format(multi_tag_accuracy))
    print("unseen word accuracy: {0:.4f}".format(unseen_words_accuracy))

    #Test the viterbi algorithm
    train_set = utils.load_dataset('data/brown-training.txt')
    dev_set = utils.load_dataset('data/brown-test.txt')
    predicted = submitted.viterbi(utils.strip_tags(dev_set), train_set)
    accuracy, _, _ = utils.evaluate_accuracies(predicted, dev_set)
    multi_tag_accuracy, unseen_words_accuracy, = utils.specialword_accuracies(train_set, predicted, dev_set)

    print("accuracy: {0:.4f}".format(accuracy))
    print("multi-tag accuracy: {0:.4f}".format(multi_tag_accuracy))
    print("unseen word accuracy: {0:.4f}".format(unseen_words_accuracy))